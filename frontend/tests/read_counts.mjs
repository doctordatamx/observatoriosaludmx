import {readFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {aggregate,readCube} from '../src/aggregate.ts';

const [path, rawFilters]=process.argv.slice(2);
const filters=JSON.parse(rawFilters);
const cube=readCube(JSON.parse(gunzipSync(readFileSync(path))),filters.municipalCube);
process.stdout.write(JSON.stringify(aggregate(cube,filters)));
