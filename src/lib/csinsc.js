var $builtinmodule = function(name)
{
    var mod = {};
        
    mod.Colour = Sk.misceval.buildClass(mod, function($gbl, $loc) {
        $loc.reset = new Sk.builtin.str("\u001b[ 0;2;0;0;0 m");
        $loc.red = new Sk.builtin.str("\u001b[ 38;2;255;0;0 m");
        $loc.black = new Sk.builtin.str("\u001b[ 38;2;0;0;0 m");
        $loc.white = new Sk.builtin.str("\u001b[ 38;2;255;255;255 m");
        $loc.grey = new Sk.builtin.str("\u001b[ 38;2;128;128;128 m");
        $loc.red = new Sk.builtin.str("\u001b[ 38;2;255;0;0 m");
        $loc.green = new Sk.builtin.str("\u001b[ 38;2;0;255;0 m");
        $loc.blue = new Sk.builtin.str("\u001b[ 38;2;0;0;255 m");
        $loc.cyan = new Sk.builtin.str("\u001b[ 38;2;0;255;255 m");
        $loc.yellow = new Sk.builtin.str("\u001b[ 38;2;255;255;0 m");
        $loc.magenta = new Sk.builtin.str("\u001b[ 38;2;255;0;255 m");
        $loc.orange = new Sk.builtin.str("\u001b[ 38;2;255;165;0 m");
        $loc.purple = new Sk.builtin.str("\u001b[ 38;2;127;0;255 m");        
    }, 'Colour', []);
    
    mod.Highlight = Sk.misceval.buildClass(mod, function($gbl, $loc) {
        $loc.black = new Sk.builtin.str("\u001b[ 48;2;0;0;0 m");
        $loc.white = new Sk.builtin.str("\u001b[ 48;2;255;255;255 m");
        $loc.grey = new Sk.builtin.str("\u001b[ 48;2;128;128;128 m");
        $loc.red = new Sk.builtin.str("\u001b[ 48;2;255;0;0 m");
        $loc.green = new Sk.builtin.str("\u001b[ 48;2;0;255;0 m");
        $loc.blue = new Sk.builtin.str("\u001b[ 48;2;0;0;255 m");    
        $loc.cyan = new Sk.builtin.str("\u001b[ 48;2;0;255;255 m");
        $loc.yellow = new Sk.builtin.str("\u001b[ 48;2;255;255;0 m");
        $loc.magenta = new Sk.builtin.str("\u001b[ 48;2;255;0;255 m");
        $loc.orange = new Sk.builtin.str("\u001b[ 48;2;255;165;0 m");
        $loc.purple = new Sk.builtin.str("\u001b[ 48;2;127;0;255 m");   
    }, 'Highlight', []);   

    mod.Style = Sk.misceval.buildClass(mod, function($gbl, $loc) {
        $loc.bold = new Sk.builtin.str("\u001b[ 1;2;0;0;0 m");    
        $loc.italics = new Sk.builtin.str("\u001b[ 3;2;0;0;0 m");    
        $loc.underline = new Sk.builtin.str("\u001b[ 4;2;0;0;0 m");    
    }, 'Style', []); 
    
    var synth = window.speechSynthesis;
    var voices = [];
	
	mod.listening = false;
	mod.speechRecognition = null;
	mod.final_transcript = "";
	mod.interim_transcript = "";
    
    function populateVoiceList() {
      voices = synth.getVoices();
    }    
    
    populateVoiceList();
    if (speechSynthesis.onvoiceschanged !== undefined) {
      speechSynthesis.onvoiceschanged = populateVoiceList;
    }
    
    mod.say = new Sk.builtin.func((text, voice) => {        
        
        var utterThis = new SpeechSynthesisUtterance(text);
		if (voice >= voices.length)
			voice = 0;
        utterThis.voice = voices[voice];
        utterThis.pitch = 1;
        utterThis.rate = 1;
        synth.speak(utterThis);        
        
        return new Sk.builtin.none;        
    });
	
	mod.isListening = new Sk.builtin.func(() => {   
		return new Sk.builtin.bool(mod.listening);
	});
	
	mod.getFinalTranscript = new Sk.builtin.func(() => {   
		return new Sk.builtin.str(mod.final_transcript);
	});
	
	mod.listen = new Sk.builtin.func(() => {        
        
		if ("webkitSpeechRecognition" in window) {
			if (mod.listening) {
				mod.speechRecognition.stop();
			}
			mod.listening = true;
			mod.final_transcript = "";
				
			mod.speechRecognition = new webkitSpeechRecognition();
			
			mod.speechRecognition.continuous = true;
			mod.speechRecognition.interimResults = true;
			mod.speechRecognition.lang = "en-AU";

			mod.speechRecognition.onerror = () => {
				console.log("Speech Recognition Error");
			};
			mod.speechRecognition.onend = () => {
				console.log("Speech Recognition Ended");
				console.log("Final transcript" + mod.final_transcript)
			};

			mod.speechRecognition.onresult = (event) => {
				mod.interim_transcript = "";

				for (let i = event.resultIndex; i < event.results.length; ++i) {
				  if (event.results[i].isFinal) {
					mod.final_transcript += event.results[i][0].transcript;
					mod.speechRecognition.stop();
					mod.listening = false;
				  } else {
					mod.interim_transcript += event.results[i][0].transcript;
				  }
				}
			};
			
			mod.speechRecognition.start();
		} else {
		  console.log("Speech Recognition Not Available");
		} 
        
        return new Sk.builtin.none;        
    });

    
    return mod;
}