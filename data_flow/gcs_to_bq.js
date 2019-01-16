/**
 * A transform which adds a field to the incoming data.
 * @param {string} inJson
 * @return {string} outJson
 */
function transform(line) {
var values = line.split(',');

var obj = new Object();
obj.bus_count = values[0];
obj.day_of_week = values[1];
obj.description = values[2];
obj.east = values[3];
obj.hour = values[4];
obj.month = values[5];
obj.north = values[6];
obj.num_reads = values[7];
obj.record_id = values[8];
obj.region = values[9];
obj.region_id = values[10];
obj.south = values[11];
obj.speed = values[12];
obj.time = values[13];
obj.west = values[14];
var jsonString = JSON.stringify(obj);

return jsonString;
}