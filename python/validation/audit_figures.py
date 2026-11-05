"""Compare figures calculated by the dashboard with an independent Silver SQL query."""
import hashlib
import json
from pathlib import Path
import subprocess

import duckdb

ROOT = Path(__file__).resolve().parents[2]
PARQUET = ROOT / "data/silver/defunciones/2024/selected.parquet"
DATA = ROOT / "frontend/public/data"
REPORT = ROOT / "docs/AUDITORIA_CIFRAS.md"
SQL = r"""
with normalized as (
 select case when regexp_full_match(ent_resid,'[0-9]{1,2}')
             then lpad(ent_resid,2,'0') else '??' end as state,
        case when regexp_full_match(trim(mun_resid),'[0-9]{1,3}')
             then lpad(trim(mun_resid),3,'0') else '???' end as municipality,
        case when sexo in ('1','2','3') then cast(sexo as int) else 9 end as sex,
        case when not list_contains($ages,edad) then 19
             when try_cast(edad as int) between 1000 and 3999 then 0
             when try_cast(edad as int) = 4000 then 0
             when try_cast(edad as int) between 4001 and 4004 then 1
             when try_cast(edad as int) between 4005 and 4084 then cast(floor((cast(edad as int)-4000)/5) as int)+1
             when try_cast(edad as int) between 4085 and 4120 then 18 else 19 end as age,
        case when try_cast(mes_regis as int) between 1 and 12
             then cast(mes_regis as int) else 0 end as month,
        upper(replace(trim(causa_def),'.','')) as code
 from read_parquet($source)
), prepared as (
 select state, state || municipality as municipality, sex, age, month,
        case when regexp_full_match(code,'[A-Z][0-9]{2}[A-Z0-9]?')
             then left(code,3) else 'SIN_CODIGO' end as cause
 from normalized
)
select state, municipality, sex, age, month, cause, count(*) as n
from prepared
where ($state='' or state=$state) and ($municipality='' or municipality=$municipality)
  and ($sex='' or cast(sex as varchar)=$sex) and ($age='' or cast(age as varchar)=$age)
  and ($cause='' or cause=$cause)
group by all
"""


def compare(connection, ages, **filters):
    scope = dict(state="", municipality="", sex="", age="", cause="") | filters
    municipal = bool(scope["state"])
    cube = DATA / (f"municipal/defunciones-2024/{scope['state']}.json.gz" if municipal else "defunciones-2024.json.gz")
    frontend = json.loads(subprocess.check_output([
        "node", str(ROOT / "frontend/tests/read_counts.mjs"), str(cube),
        json.dumps(scope | {"municipalCube": municipal}),
    ], encoding="utf-8"))
    expected = dict(total=0, temporal=[0]*13, ages=[0]*20, men=[0]*20, women=[0]*20,
                    sexes={}, territories={}, municipalities={}, causes={}, heat=[[0]*13 for _ in range(20)])
    for state, municipality, sex, age, month, cause, count in connection.execute(
        SQL, scope | dict(ages=ages, source=str(PARQUET))
    ).fetchall():
        expected["total"] += count
        expected["temporal"][month] += count
        expected["ages"][age] += count
        expected["heat"][age][month] += count
        if sex == 1:
            expected["men"][age] += count
        if sex == 2:
            expected["women"][age] += count
        for field, key in [("sexes", str(sex)), ("territories", state), ("causes", cause)]:
            values = expected[field]
            values[key] = values.get(key, 0) + count
        if municipal:
            values = expected["municipalities"]
            values[municipality] = values.get(municipality, 0) + count
    assert sum(frontend["causes"].values()) == frontend["total"]
    assert sum(frontend["territories"].values()) == frontend["total"]
    if municipal:
        assert sum(frontend["municipalities"].values()) == frontend["total"]
    return frontend, expected, cube


def main():
    labels = json.loads((ROOT / "config/catalogue_labels.json").read_text(encoding="utf-8"))
    ages = list(labels["death_ages_by_year"]["2024"])
    cases = [
        ("Nacional, todos los filtros", {}, "total", None),
        ("Nuevo León, entidad 19", {"state": "19"}, "total", None),
        ("Monterrey, municipio 19039", {"state": "19", "municipality": "19039"}, "total", None),
        ("Mujeres, edad 65–69, E11, Nuevo León", {"state": "19", "sex": "2", "age": "14", "cause": "E11"}, "total", None),
        ("Nacional, mujeres de 65–69 años", {}, "women", 14),
        ("Nacional, mes de registro enero", {}, "temporal", 1),
        ("Nacional, diagnóstico E11", {}, "causes", "E11"),
    ]
    lines = [
        "# Auditoría de cifras", "",
        "Mortalidad registrada DGIS/INEGI, año de registro 2024, residencia habitual. "
        "La columna frontend ejecuta la función que alimenta el tablero local. La referencia usa DuckDB sobre "
        "`data/silver/defunciones/2024/selected.parquet` y el catálogo etario 2024. "
        "La edición pública informa indisponibilidad y carece de cifras epidemiológicas visibles.", "",
        "| Consulta | Frontend | SQL | Diferencia absoluta | Diferencia relativa | Agregado y SHA-256 | Resultado |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    cache = {}
    failed = False
    with duckdb.connect() as connection:
        for label, filters, field, key in cases:
            signature = tuple(filters.items())
            if signature not in cache:
                cache[signature] = compare(connection, ages, **filters)
            observed, expected, cube = cache[signature]
            a, b = observed[field], expected[field]
            if key is not None:
                a, b = a[key], b[key]
            delta = abs(a-b)
            relative = f"{100*delta/abs(b):.4f} %" if b else "No aplica"
            equal = observed == expected
            failed |= not equal
            with cube.open("rb") as stream:
                sha = hashlib.file_digest(stream, "sha256").hexdigest()
            lines.append(f"| {label} | {a:,} | {b:,} | {delta:,} | {relative} | "
                         f"`{cube.relative_to(DATA).as_posix()}` · `{sha}` | {'Coincide' if equal else 'Diverge'} |")
    lines += ["", "Cada consulta compara además todas sus celdas de edad, sexo, causa, territorio y mes, "
              "incluidos los códigos desconocidos. Para la participación se valida que los conteos de las "
              "categorías exhaustivas sumen el denominador filtrado. Las tablas de categorías principales "
              "muestran un subconjunto y sus porcentajes redondeados pueden sumar menos de 100 %.", "",
              "Regenerar desde la raíz con `python python/validation/audit_figures.py`. "
              "Este contraste de visualizaciones cubre mortalidad 2024. La auditoría Bronze–Silver–Gold "
              "y las pruebas existentes cubren los totales y consultas adicionales de otras series.", ""]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    return failed


if __name__ == "__main__":
    raise SystemExit(main())
