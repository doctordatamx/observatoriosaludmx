"""Populate the Pages build with synthetic fixtures only."""
import gzip
import json
from pathlib import Path
from shutil import copytree

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "frontend" / "dist-pages"
STATES = {f"{i:02}": f"Entidad ficticia {i}" for i in range(1, 7)}
CAUSES = {"E11": "Diabetes mellitus tipo 2", "I10": "Hipertensión esencial", "J18": "Neumonía"}
MONTHS = list(range(1, 13))
AGES = ["<1", "1–4", *[f"{i}–{i+4}" for i in range(5, 85, 5)], "85+", "Sin dato válido"]


def write(path, value):
    file = OUTPUT / path
    file.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode()
    file.write_bytes(gzip.compress(content, mtime=0) if file.suffix == ".gz" else content)


def feature(code, name, x, y):
    ring = [[x, y], [x+1, y], [x+1, y+1], [x, y+1], [x, y]]
    return dict(type="Feature", properties=dict(name=code, cvegeo=code, nomgeo=name),
                geometry=dict(type="Polygon", coordinates=[ring]))


def collection(features):
    return dict(type="FeatureCollection", features=features)


def build():
    if not (OUTPUT / "index.html").is_file():
        raise SystemExit("Ejecuta primero vite build --mode pages.")
    copytree(ROOT / "frontend" / "public" / "docs", OUTPUT / "docs", dirs_exist_ok=True)
    (OUTPUT / ".nojekyll").touch()
    datasets, partitions, eligible, lab_datasets = [], {}, {}, []
    state_codes = list(STATES)
    municipal_codes = ["01001", "01002"]
    municipal_names = dict(zip(municipal_codes, ["Municipio ficticio A", "Municipio ficticio B"]))
    write("geo/index.json", dict(states=STATES, names=municipal_names, available_states=["01"],
                                vintage="Geometría esquemática ficticia"))
    write("geo/states.json.gz", collection([
        feature(code, name, i % 3 * 1.05, i // 3 * 1.05)
        for i, (code, name) in enumerate(STATES.items())
    ]))
    write("geo/municipalities-01.json.gz", collection([
        feature(code, name, i * 1.05, 0)
        for i, (code, name) in enumerate(municipal_names.items())
    ]))
    for source_index, source in enumerate(["defunciones", "egresos", "urgencias", "lesiones", "sectorial"]):
        for year in range(2020, 2025):
            dataset_id = f"{source}-{year}"
            filename = dataset_id + ".json.gz"
            rows = []
            for state in range(len(STATES)):
                for sex in (1, 2):
                    for age in range(19):
                        for month in MONTHS:
                            for cause in range(len(CAUSES)):
                                trend = (year-2020) * (cause+1)
                                variation = (month*(source_index+1) + age + sex + cause*state) % 13
                                count = 2 + trend + variation + age//4 + state + source_index
                                rows.append([state, sex, age, month, cause, count])
            total = sum(row[5] for row in rows)
            geography = "Entidades ficticias"
            coverage = "Datos simulados"
            dataset = dict(id=dataset_id, source=source, year=year)
            datasets.append(dict(**dataset, total=total, coverage=coverage, geography=geography,
                                 calendar="Mes simulado", cutoffs=[], partial=False, months=MONTHS,
                                 url="", sha256="", file=filename, bytes=0, status="demo",
                                 quality=dict(records=total, cube_total=total, cube_cells=len(rows),
                                              unknown_age=0, unknown_sex=0, invalid_cause_format=0,
                                              unknown_month=0, nonstandard_state=0)))
            write("data/" + filename, dict(states=state_codes, causes=list(CAUSES), rows=rows))
            if source != "sectorial":
                local_file = f"municipal/{dataset_id}/01.json.gz"
                local_rows = [row + [0] for row in rows if row[0] == 0]
                split_rows = []
                for row in local_rows:
                    first = row[5] * 3 // 5
                    split_rows.extend([row[:5] + [first, 0], row[:5] + [row[5]-first, 1]])
                write("data/" + local_file, dict(states=["01"], causes=list(CAUSES),
                                                municipalities=municipal_codes, rows=split_rows))
                partitions[dataset_id] = {"states": {"01": dict(file=local_file, total=sum(r[5] for r in local_rows),
                                                              unmatched_geometry=0)}}
                eligible[dataset_id] = municipal_codes
            lab_datasets.append(dataset)
            groupings = {2: [1, 1, 1, 1, 2, 2], 3: [1, 1, 2, 2, 3, 3], 4: [1, 1, 2, 3, 4, 4]}
            write(f"data/lab/{dataset_id}.json", dict(
                **dataset, geography=geography, coverage="Resultados ilustrativos", entities=len(STATES),
                sha256="", cluster_codes=list(CAUSES),
                clusters=[dict(k=k, silhouette=.55, stability=.8, groups=dict(zip(state_codes, groups)))
                          for k, groups in groupings.items()],
                dendrogram=dict(labels=state_codes, order=list(range(1, 7)),
                                merge=[[-1,-2], [-5,-6], [-3,-4], [1,3], [4,2]],
                                height=[.09,.12,.2,.62,1.2]),
                mds=dict(points=[dict(state=code, x=x, y=y) for code, (x, y) in zip(
                    state_codes, [(-.75,.25),(-.6,.36),(-.25,-.37),(-.07,-.45),(.72,.16),(.91,.08)])],
                         retained=.92, distortion=.12),
                moran={}, anomalies={},
            ))
    write("data/index.json", dict(updated="", age_groups=AGES, states=STATES, causes=CAUSES, datasets=datasets))
    write("data/municipal-index.json", dict(datasets=partitions))
    write("geo/health-catalogues.json", dict(eligible=eligible))
    write("data/lab/index.json", dict(datasets=lab_datasets, vintage="esquema ficticio",
                                     minimum_records=20, queen_edges=0, rook_edges=0))


if __name__ == "__main__":
    build()
