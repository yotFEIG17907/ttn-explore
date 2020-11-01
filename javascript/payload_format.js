// This is the Decoder function invoked by TTN to process messages received from the
// sensors. This is in the Applications -> skybar-sensors page
// https://console.thethingsnetwork.org/applications/skybar-sensors/payload-formats
//
// The code is Javascript

// These are selected by bytes[2] if bytes[1] is 0x0D
var event_type = ["Periodic Report", "Temp above upper threshold", "Temp below lower threshold",
    "Temp report on change increase", "Temp report on change decrease", "Humidity above upper threshold",
    "Humidity below lower threshold", "Humidity report on change increase", "Humidity report on change decrease"];


function Decoder(bytes, port) {
  // Decode an uplink message from a buffer
  // (array) of bytes to an object of fields.
  var decoded = {};

  // if (port === 1) decoded.led = bytes[0];
  decoded.version = bytes[0] >> 4;
  decoded.pktcnt = bytes[0] & 0x0F;
  decoded.msgtype = bytes[1]
  if (bytes[1] == 0x00) {
     // Device has reset
     decoded.msgdesc = "RESET";
     decoded.event_type = "Reset";
  } else if (bytes[1] == 0x01) {
     decoded.event_type = "Supervisory";
     decoded.msgdesc = "SUPERVISORY";
     decoded.errorcodes = bytes[2]
     decoded.sensor_state = bytes[3]
     decoded.batlevel = (bytes[4] >> 4) + (bytes[4] & 0x0F) / 10.0
  } else if (bytes[1] == 0x02) {
     decoded.msgdesc = "TAMPER";
     decoded.event_type = "Tamper"
  } else if (bytes[1] == 0x0D) {
     decoded.msgdesc = "SENSOR";
     if (bytes[2] >= event_type.length) {
       decoded.event_type = "OOB_" + bytes[2];
     } else {
       decoded.event_type = event_type[bytes[2]];
     }
     decoded.sensor_event_type = bytes[2];
     var temp_c = bytes[3] & 0x7F;
     var decimal = (bytes[4] >> 4) / 10.0;
     decoded.temp_c = temp_c + decimal;
     if ((bytes[3] & 0x80) == 0x80) {
       decoded.temp_c = -decoded.temp_c;
     }
     decoded.temp_f = (decoded.temp_c * 9 / 5) + 32.0;
     var humd = bytes[5];
     var humd_dec = (bytes[4] >> 4) / 10.0;
     decoded.humidity_percent = humd + humd_dec;
  } else if (bytes[1] == 0xFB) {
     decoded.msgdesc = "LINKQ";
     decoded.event_type = "Link Quality"
  } else {
     decoded.msgdesc = "UNKNOWN";
     decoded.event_type = "Unknown"
  }

  return decoded;
}