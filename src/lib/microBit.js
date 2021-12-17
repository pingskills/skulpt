// Define the file as a Skulpt Python module
var $builtinmodule = function(name)
{  

    var ACCEL_SRV = 'e95d0753-251d-470a-a062-fa1922dfa9a8'
    var ACCEL_DATA = 'e95dca4b-251d-470a-a062-fa1922dfa9a8'
    var ACCEL_PERIOD = 'e95dfb24-251d-470a-a062-fa1922dfa9a8'
    var MAGNETO_SRV = 'e95df2d8-251d-470a-a062-fa1922dfa9a8'
    var MAGNETO_DATA = 'e95dfb11-251d-470a-a062-fa1922dfa9a8'
    var MAGNETO_PERIOD = 'e95d386c-251d-470a-a062-fa1922dfa9a8'
    var MAGNETO_BEARING = 'e95d9715-251d-470a-a062-fa1922dfa9a8'
    var BTN_SRV = 'e95d9882-251d-470a-a062-fa1922dfa9a8'
    var BTN_A_STATE = 'e95dda90-251d-470a-a062-fa1922dfa9a8'
    var BTN_B_STATE = 'e95dda91-251d-470a-a062-fa1922dfa9a8'
    var IO_PIN_SRV = 'e95d127b-251d-470a-a062-fa1922dfa9a8'
    var IO_PIN_DATA = 'e95d8d00-251d-470a-a062-fa1922dfa9a8'
    var IO_AD_CONFIG = 'e95d5899-251d-470a-a062-fa1922dfa9a8'
    var IO_PIN_CONFIG = 'e95db9fe-251d-470a-a062-fa1922dfa9a8'
    var IO_PIN_PWM = 'e95dd822-251d-470a-a062-fa1922dfa9a8'
    var LED_SRV = 'e95dd91d-251d-470a-a062-fa1922dfa9a8'
    var LED_STATE = 'e95d7b77-251d-470a-a062-fa1922dfa9a8'
    var LED_TEXT = 'e95d93ee-251d-470a-a062-fa1922dfa9a8'
    var LED_SCROLL = 'e95d0d2d-251d-470a-a062-fa1922dfa9a8'
    var TEMP_SRV = 'e95d6100-251d-470a-a062-fa1922dfa9a8'
    var TEMP_DATA = 'e95d9250-251d-470a-a062-fa1922dfa9a8'
    var TEMP_PERIOD = 'e95d1b25-251d-470a-a062-fa1922dfa9a8'
       
    class uBit {

      constructor() {
        this.accelerometer = {
          x: 0,
          y: 0,
          z: 0
        };

        this.magnetometer_raw = {
          x: 0,
          y: 0,
          z: 0
        };

        this.magnetometer_bearing = 0;
        this.temperature = 0;

        this.buttonA = 0;
        this.buttonACallBack=function(){};

        this.buttonB = 0;
        this.buttonBCallBack=function(){};

        this.connected = false;

        this.onConnectCallback=function(){};
        this.onDisconnectCallback=function(){};

        this.onBLENotifyCallback=function(){};

        this.characteristic = {
          IO_PIN_DATA: {},
          IO_AD_CONFIG: {},
          IO_PIN_CONFIG: {},
          IO_PIN_PWM: {},
          LED_STATE: {},
          LED_TEXT: {},
          LED_SCROLL: {},
        }
      }

      getTemperature() {
        return this.temperature;
      }

      getAccelerometer() {
        return this.accelerometer;
      }

      getBearing() {
        return this.magnetometer_bearing;
      }

      getButtonA() {
        return this.buttonA;
      }

      setButtonACallback(callbackFunction){
        this.buttonACallBack=callbackFunction;
      }

      getButtonB() {
        return this.buttonB;
      }

      setButtonBCallback(callbackFunction){
        this.buttonBCallBack=callbackFunction;
      }

      onConnect(callbackFunction){
        this.onConnectCallback=callbackFunction;
      }

      onDisconnect(callbackFunction){
        this.onDisconnectCallback=callbackFunction;
      }

      onBleNotify(callbackFunction){
        this.onBLENotifyCallback=callbackFunction;
      }

      writePin(pin) {
        //something like this should work, but we need to create the correct buffer
        //this.characteristic.IO_PIN_DATA.writeValue(data);
      }

      readPin(pin) {

      }

      writeMatrixIcon(icon) {
        var ledMatrix = new Int8Array(5);
        var buffer = [
          ['0', '0', '0', '0', '0', '0', '0', '0'],
          ['0', '0', '0', '0', '0', '0', '0', '0'],
          ['0', '0', '0', '0', '0', '0', '0', '0'],
          ['0', '0', '0', '0', '0', '0', '0', '0'],
          ['0', '0', '0', '0', '0', '0', '0', '0']
        ]
        for (var i = 0; i < 5; i++) {
          for (var j = 0; j < 5; j++) {
            buffer[i][7-j] = icon[i][4 - j]
          }
        }
        for (var i = 0; i < 5; i++) {
          var string = buffer[i].join("");
          ledMatrix[i]=parseInt(string,2)
        }
        if(this.connected){
          this.characteristic.LED_STATE.writeValue(ledMatrix)
          .then(_ => {
          })
          .catch(error => {
            console.log(error);
          });
        }
      }

      writeMatrixTextSpeed(speed){
        var buffer= new Uint8Array(speed);
        if(this.connected){
          this.characteristic.LED_TEXT.writeValue(buffer)
          .then(_ => {
          })
          .catch(error => {
            console.log(error);
          });
        }
      }

      writeMatrixText(str){
        var buffer= new Uint8Array(toUTF8Array(str));
        if(this.connected){
          this.characteristic.LED_TEXT.writeValue(buffer)
          .then(_ => {
          })
          .catch(error => {
            console.log(error);
          });
        }
      }

      onButtonA(){
        this.buttonACallBack();
      }

      onButtonB(){
        this.buttonBCallBack();
      }

      characteristic_updated(event) {

        
        //BUTTON CHARACTERISTIC
        if (event.target.uuid == BTN_A_STATE) {
          //console.log("BTN_A_STATE", event.target.value.getInt8());
          this.buttonA = event.target.value.getInt8();
          if (this.buttonA){
            this.onButtonA();
          }
        }

        if (event.target.uuid == BTN_B_STATE) {
          //console.log("BTN_B_STATE", event.target.value.getInt8());
          this.buttonB = event.target.value.getInt8();
          if (this.buttonB){
            this.onButtonB();
          }
        }

        //ACCELEROMETER CHARACTERISTIC
        if (event.target.uuid == ACCEL_DATA) {
          //true is for reading the bits as little-endian
          //console.log("ACCEL_DATA_X", event.target.value.getInt16(0,true));
          //console.log("ACCEL_DATA_Y", event.target.value.getInt16(2,true));
          //console.log("ACCEL_DATA_Z", event.target.value.getInt16(4,true));
          this.accelerometer.x = event.target.value.getInt16(0, true);
          this.accelerometer.y = event.target.value.getInt16(2, true);
          this.accelerometer.z = event.target.value.getInt16(4, true);
        }

        // MAGNETOMETER CHARACTERISTIC (raw data)
        if (event.target.uuid == MAGNETO_DATA) {
          //  console.log("MAGNETO_DATA_X", event.target.value.getInt16(0,true));
          //  console.log("MAGNETO_DATA_Y", event.target.value.getInt16(2,true));
          //  console.log("MAGNETO_DATA_Z", event.target.value.getInt16(4,true));
          this.magnetometer_raw.x = event.target.value.getInt16(0, true);
          this.magnetometer_raw.y = event.target.value.getInt16(2, true);
          this.magnetometer_raw.z = event.target.value.getInt16(4, true);
        }

        // MAGNETOMETER CHARACTERISTIC (bearing)
        if (event.target.uuid == MAGNETO_BEARING) {
          //console.log("BEARING", event.target.value.getInt16(0,true));
          this.magnetometer_bearing = event.target.value.getInt16(0, true);
        }

        // TEMPERATURE CHARACTERISTIC
        if (event.target.uuid == TEMP_DATA) {
          //console.log("TEMP_DATA", event.target.value.getInt8());
          this.temperature = event.target.value.getInt8();

        }
        
        this.onBLENotifyCallback();
      }

      searchDevice() {
        filters: []
        var options = {};
        options.acceptAllDevices = true;
        options.optionalServices = [ACCEL_SRV, MAGNETO_SRV, BTN_SRV, IO_PIN_SRV, LED_SRV, TEMP_SRV];

        console.log('Requesting Bluetooth Device...');
        console.log('with ' + JSON.stringify(options));

        navigator.bluetooth.requestDevice(options)
        .then(device => {

          console.log('> Name:             ' + device.name);
          console.log('> Id:               ' + device.id);

          device.addEventListener('gattserverdisconnected', this.onDisconnectCallback);

          // Attempts to connect to remote GATT Server.
          return device.gatt.connect();

        })
        .then(server => {
          // Note that we could also get all services that match a specific UUID by
          // passing it to getPrimaryServices().
          this.onConnectCallback();
          console.log('Getting Services...');
          return server.getPrimaryServices();
        })
        .then(services => {
          console.log('Getting Characteristics...');
          let queue = Promise.resolve();
          services.forEach(service => {
            queue = queue.then(_ => service.getCharacteristics().then(characteristics => {
              console.log('> Service: ' + service.uuid);
              characteristics.forEach(characteristic => {
                console.log('>> Characteristic: ' + characteristic.uuid + ' ' +
                  getSupportedProperties(characteristic));

                //need to store all the characteristic I want to write to be able to access them later.
                switch (characteristic.uuid) {
                  case IO_PIN_DATA:
                    this.characteristic.IO_PIN_DATA = characteristic;
                    break;

                  case IO_AD_CONFIG:
                    this.characteristic.IO_AD_CONFIG = characteristic;
                    break;

                  case IO_PIN_CONFIG:
                    this.characteristic.IO_PIN_CONFIG = characteristic;
                    break;

                  case IO_PIN_PWM:
                    this.characteristic.IO_PIN_PWM = characteristic;
                    break;

                  case LED_STATE:
                    this.characteristic.LED_STATE = characteristic;
                    this.connected = true;

                    break;

                  case LED_TEXT:
                    this.characteristic.LED_TEXT = characteristic;
                    break;

                  case LED_SCROLL:
                    this.characteristic.LED_SCROLL = characteristic;
                    break;

                  default:

                }


                if (getSupportedProperties(characteristic).includes('NOTIFY')) {
                  characteristic.startNotifications().catch(err => console.log('startNotifications', err));
                  characteristic.addEventListener('characteristicvaluechanged',
                    this.characteristic_updated.bind(this));
                }
              });
            }));
          });
          return queue;
        }
      )
        .catch(error => {
          console.log('Argh! ' + error);
        });
      }
    }


    /* Utils */

    function isWebBluetoothEnabled() {
      if (navigator.bluetooth) {
        return true;
      } else {
        ChromeSamples.setStatus('Web Bluetooth API is not available.\n' +
          'Please make sure the "Experimental Web Platform features" flag is enabled.');
        return false;
      }
    }


    function getSupportedProperties(characteristic) {
      let supportedProperties = [];
      for (const p in characteristic.properties) {
        if (characteristic.properties[p] === true) {
          supportedProperties.push(p.toUpperCase());
        }
      }
      return '[' + supportedProperties.join(', ') + ']';
    }

    function toUTF8Array(str) {
        var utf8 = [];
        for (var i=0; i < str.length; i++) {
            var charcode = str.charCodeAt(i);
            if (charcode < 0x80) utf8.push(charcode);
            else if (charcode < 0x800) {
                utf8.push(0xc0 | (charcode >> 6),
                          0x80 | (charcode & 0x3f));
            }
            else if (charcode < 0xd800 || charcode >= 0xe000) {
                utf8.push(0xe0 | (charcode >> 12),
                          0x80 | ((charcode>>6) & 0x3f),
                          0x80 | (charcode & 0x3f));
            }
            // surrogate pair
            else {
                i++;
                // UTF-16 encodes 0x10000-0x10FFFF by
                // subtracting 0x10000 and splitting the
                // 20 bits of 0x0-0xFFFFF into two halves
                charcode = 0x10000 + (((charcode & 0x3ff)<<10)
                          | (str.charCodeAt(i) & 0x3ff));
                utf8.push(0xf0 | (charcode >>18),
                          0x80 | ((charcode>>12) & 0x3f),
                          0x80 | ((charcode>>6) & 0x3f),
                          0x80 | (charcode & 0x3f));
            }
        }
        return utf8;
    }
    
    var iconLeft = [
      ['0', '0', '0', '0', '0'],
      ['0', '1', '0', '1', '0'],
      ['0', '0', '0', '0', '0'],
      ['1', '0', '0', '0', '1'],
      ['0', '1', '1', '1', '0']
    ]

    var iconRight = [
      ['0', '0', '0', '0', '0'],
      ['0', '1', '0', '1', '0'],
      ['0', '0', '0', '0', '0'],
      ['0', '1', '1', '1', '0'],
      ['1', '0', '0', '0', '1']
    ]    


    var mod = {};
    
    mod.Microbit = Sk.misceval.buildClass(mod, function($gbl, $loc) {
        $loc.__init__ = new Sk.builtin.func(function(self) {         
            filters: []
            var options = {};
            options.acceptAllDevices = true;
            options.optionalServices = [ACCEL_SRV, MAGNETO_SRV, BTN_SRV, IO_PIN_SRV, LED_SRV, TEMP_SRV];

            console.log('Requesting Bluetooth Device...');
            console.log('with ' + JSON.stringify(options));

            self.microBit = new uBit();
			
			self.writableHandle = null;
			self.interval = null;
			self.isRecording = false;
			
			self.recordButtonA = async function() {
				if (self.writableHandle !== null)
				{
					await self.writableHandle.write(new Date().toLocaleString() + ",A\n");
				}
			};
			
			self.recordButtonB = async function() {
				if (self.writableHandle !== null)
				{
					await self.writableHandle.write(new Date().toLocaleString() + ",B\n");
				}
			};
                       

			self.stopRecordData = async function()
			{
				if (self.interval !== null)
				{
					window.clearInterval(self.interval);
					self.interval = null;
				}
				if (self.writableHandle !== null)
				{
					// Close the file and write the contents to disk.
					await self.writableHandle.close();
					self.writableHandle = null;
				}
				self.isRecording = false;
			}
			
			self.recordTemp = async function()
			{
				await self.writableHandle.write(new Date().toLocaleString() + "," + self.microBit.temperature + "\n");
			}
			
			self.recordAccelerometer = async function()
			{
				await self.writableHandle.write(new Date().toLocaleString() + "," + self.microBit.accelerometer.x + "," + self.microBit.accelerometer.y + "," + self.microBit.accelerometer.z + "\n");
			}
			
			self.microBit.setButtonACallback(self.recordButtonA);
			
			self.microBit.setButtonBCallback(self.recordButtonB);
			
			
			self.recordDataFunc = async function(interval)
			{
			  const options = {
				suggestedName: filename,
				types: [
				  {
					
					description: 'Text Files',
					accept: {
					  'text/plain': ['.txt'],
					},
				  },
				],
			  };
			  const fileHandle = await window.showSaveFilePicker(options);
			  
			  self.writableHandle = await fileHandle.createWritable();
			  
			  if (interval > 0)
			  {
				  //self.interval = window.setInterval(self.recordTemp, interval);
				  self.interval = window.setInterval(self.recordAccelerometer, interval);
			  }
			  self.isRecording = true;
			}			

            navigator.bluetooth.requestDevice(options)
            .then(device => {

                self.device = device;
                console.log('> Name:             ' + device.name);
                console.log('> Id:               ' + device.id);

                // Attempts to connect to remote GATT Server.
                return device.gatt.connect();

            })
            .then(server => {
              // Note that we could also get all services that match a specific UUID by
              // passing it to getPrimaryServices().
              console.log('Getting Services...');
              return server.getPrimaryServices();
            })
            .then(services => {
              console.log('Getting Characteristics...');
              let queue = Promise.resolve();
              services.forEach(service => {
                queue = queue.then(_ => service.getCharacteristics().then(characteristics => {
                  console.log('> Service: ' + service.uuid);
                  characteristics.forEach(characteristic => {
                    console.log('>> Characteristic: ' + characteristic.uuid + ' ' +
                      getSupportedProperties(characteristic));

                    //need to store all the characteristic I want to write to be able to access them later.
                    switch (characteristic.uuid) {
                      case IO_PIN_DATA:
                        self.microBit.characteristic.IO_PIN_DATA = characteristic;
                        break;

                      case IO_AD_CONFIG:
                        self.microBit.characteristic.IO_AD_CONFIG = characteristic;
                        break;

                      case IO_PIN_CONFIG:
                        self.microBit.characteristic.IO_PIN_CONFIG = characteristic;
                        break;

                      case IO_PIN_PWM:
                        self.microBit.characteristic.IO_PIN_PWM = characteristic;
                        break;

                      case LED_STATE:
                        self.microBit.characteristic.LED_STATE = characteristic;
                        self.microBit.connected = true;

                        break;

                      case LED_TEXT:
                        self.microBit.characteristic.LED_TEXT = characteristic;
                        break;

                      case LED_SCROLL:
                        self.microBit.characteristic.LED_SCROLL = characteristic;
                        break;

                      default:
                    }

                    if (getSupportedProperties(characteristic).includes('NOTIFY')) {
                      characteristic.startNotifications().catch(err => console.log('startNotifications', err));
                      characteristic.addEventListener('characteristicvaluechanged',
                        self.microBit.characteristic_updated.bind(self.microBit));
                    }
                  });
                }));
              });
              
              
              return queue;
            })
            .catch(error => {
              console.log('Argh! ' + error);
            });

            return;
        });
    
        $loc.setText = new Sk.builtin.func((self, scrollText) => {
          var text = "" + scrollText;
          console.log("Updating Scrolling text:" + text);
          self.microBit.writeMatrixText(text);
          return new Sk.builtin.none;  
        });      

        $loc.isConnected = new Sk.builtin.func((self) => {
            return new Sk.builtin.bool(self.microBit.connected);   
        });
        
        $loc.getName = new Sk.builtin.func((self) => {
            return new Sk.builtin.str(self.device.name);
        });
        
        $loc.getButtonA = new Sk.builtin.func((self) => {
            return new Sk.builtin.int_(self.microBit.buttonA);
        });
		
        $loc.getButtonB = new Sk.builtin.func((self) => {
            return new Sk.builtin.int_(self.microBit.buttonB);
        });
		
		$loc.getTemperature = new Sk.builtin.func((self) => {
            return new Sk.builtin.int_(self.microBit.temperature);
        });
		
		$loc.getBearing = new Sk.builtin.func((self) => {
            return new Sk.builtin.int_(self.microBit.magnetometer_bearing);
        });
		
		$loc.getAccelerometerX = new Sk.builtin.func((self) => {
            return new Sk.builtin.int_(self.microBit.accelerometer.x);
        });
		
		$loc.getAccelerometerY = new Sk.builtin.func((self) => {
            return new Sk.builtin.int_(self.microBit.accelerometer.y);
        });
		
		$loc.getAccelerometerZ = new Sk.builtin.func((self) => {
            return new Sk.builtin.int_(self.microBit.accelerometer.z);
        });
		
		$loc.recordData = new Sk.builtin.func((self, interval) => {
			let modal = document.querySelector(".modal");
			let closeBtn = document.querySelector(".close-btn");
			let okBtn = document.querySelector(".ok-btn");
			
			modal.style.display = "block";
			
			closeBtn.onclick = function(){
			  modal.style.display = "none";
			}
			okBtn.onclick = function(){
			  modal.style.display = "none";
			  self.recordDataFunc(interval);
			}
        });
		
		$loc.stopRecordData = new Sk.builtin.func((self) => {
			self.stopRecordData();
        });
		
		$loc.isRecording = new Sk.builtin.func((self) => {
			return new Sk.builtin.bool(self.isRecording);  
		});

    },
    'Microbit', []);

    
    mod.isConnected = new Sk.builtin.bool(false); 
    mod.buttonA = new Sk.builtin.int_(0);
    mod.buttonB = new Sk.builtin.int_(0);
    
    mod.accX = new Sk.builtin.float_(0);
    mod.accY = new Sk.builtin.float_(0);
    mod.accZ = new Sk.builtin.float_(0);
    mod.temp = new Sk.builtin.float_(0);
    mod.bearing = new Sk.builtin.float_(0);
    
    mod.microBit = new uBit();

    mod.microBit.onConnect(function(){
      console.log("connected");

      //document.getElementById("connected").innerHTML="true";
      //document.getElementById("properties").classList.toggle('inactive');

      mod.microBit.setButtonACallback(function(){
        console.log("buttonA pressed");
      });

      mod.microBit.setButtonBCallback(function(){
        console.log("buttonB pressed");
      });
      
      mod.isConnected = new Sk.builtin.bool(true); 
    });

    mod.microBit.onDisconnect(function(){
      console.log("disconnected");
      //document.getElementById("connected").innerHTML="false";
    });
        
    mod.microBit.onBleNotify(function(){
      //document.getElementById("buttonA").innerHTML=microBit.getButtonA();
      //document.getElementById("buttonB").innerHTML=microBit.getButtonB();

      //document.getElementById("acc_X").innerHTML=microBit.getAccelerometer().x;
      //document.getElementById("acc_Y").innerHTML=microBit.getAccelerometer().y;
      //document.getElementById("acc_Z").innerHTML=microBit.getAccelerometer().z;

      //document.getElementById("temp").innerHTML=microBit.getTemperature();
      //document.getElementById("bearing").innerHTML=microBit.getBearing();
        mod.buttonA = new Sk.builtin.int_(mod.microBit.buttonA);
        mod.buttonB = new Sk.builtin.int_(mod.microBit.buttonB);
        mod.accX = new Sk.builtin.float_(mod.microBit.getAccelerometer().x);
        mod.accY = new Sk.builtin.float_(mod.microBit.getAccelerometer().y);
        mod.accZ = new Sk.builtin.float_(mod.microBit.getAccelerometer().z);
        mod.temp = new Sk.builtin.float_(mod.microBit.getTemperature());
        mod.bearing = new Sk.builtin.float_(mod.microBit.getBearing());      
    })   
   
    mod.getAccelerometer = new Sk.builtin.func(() => {
      return new Sk.builtin.list([new Sk.builtin.int_(mod.microBit.getAccelerometer().x), new Sk.builtin.int_(mod.microBit.getAccelerometer().y), new Sk.builtin.int_(mod.microBit.getAccelerometer().z)]);   
    });   

    mod.getBearing = new Sk.builtin.func(() => {
      return new Sk.builtin.float_(mod.microBit.getBearing());   
    }); 

    mod.getButtonA = new Sk.builtin.func(() => {
      return new Sk.builtin.int_(mod.microBit.buttonA);   
    });   

    mod.getButtonB = new Sk.builtin.func(() => {
      return new Sk.builtin.int_(mod.microBit.buttonB);   
    });       
    
    //function searchDevice(){
    mod.searchDevice = new Sk.builtin.func(() => {
      mod.microBit.searchDevice();
    });    

    var ledMatrix = [
      ['0', '0', '0', '0', '0'],
      ['0', '0', '0', '0', '0'],
      ['0', '0', '0', '0', '0'],
      ['0', '0', '0', '0', '0'],
      ['0', '0', '0', '0', '0']
    ]

    //function updatePixel(x,y,value){
    mod.updatePixel = new Sk.builtin.func((x, y, value) => {
      if (value){
        ledMatrix[x][y]=1;
      }else{
        ledMatrix[x][y]=0;
      }
      mod.microBit.writeMatrixIcon(ledMatrix);
      
      return new Sk.builtin.none;  
    });
   
    mod.isConnected = new Sk.builtin.func(() => {
       return new Sk.builtin.bool(mod.microBit.connected);   
    });
       
    mod.updateText = new Sk.builtin.func((scrollText) => {
      //text=document.getElementById("newText").value;
      var text = "" + scrollText;
      console.log("Updating Scrolling text:" + text);
      mod.microBit.writeMatrixText(text);
      return new Sk.builtin.none;  
    });    
    
    return mod;
}