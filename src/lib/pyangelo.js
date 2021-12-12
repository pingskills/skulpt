// src/lib/pyangelo.js
//  

// Define the file as a Skulpt Python module
var $builtinmodule = function(name)
{      
    var mod = {};
    
    var canvas = document.getElementById("pyangelo");
    var ctx = canvas.getContext('2d'); 
    
    var _keysUp = {};
    var _keysDown = {};
    
    var _commands = [];
    var _activeCommands = null;
     
    var colours = {};
    colours[Sk.builtins.BLACK] = "rgba(0, 0, 0, 1)";
    colours[Sk.builtins.WHITE] = "rgba(255, 255, 255, 1)";
    colours[Sk.builtins.RED] = "rgba(255, 0, 0, 1)";
    colours[Sk.builtins.GREEN] = "rgba(0, 255, 0, 1)";
    colours[Sk.builtins.BLUE] = "rgba(0, 0, 255, 1)";
    
    mod.width = new Sk.builtin.int_(canvas.width);
    mod.height = new Sk.builtin.int_(canvas.height);
    
    canvas.addEventListener("keydown", _keyDownListener);
    canvas.addEventListener("keyup", _keyUpListener);
    
    ctx.font = "30px Consolas";
       
    startTime = new Date();
        
    Sk.builtins.animationFrameRequest = window.requestAnimationFrame(render);
    
    function render(timestamp) {
        
        if (_activeCommands != null)
        {
            while (_activeCommands.length > 0)
            {
                command = _activeCommands.shift();
                
                command[0].call(mod, command[1]);
            }            
        }
        req = window.requestAnimationFrame(render);
        
        // to enable the client to cancel the animation request
        Sk.builtins.animationFrameRequest = req;
        _activeCommands = null;        
    }
    
    mod.timeElapsed = function ()
    {
        endTime = new Date();
        result = (endTime - startTime) / 1000;
        startTime = endTime;
        
        return new Sk.builtin.float_(result);
    }

    function _clearScreen(args)
    {        
        ctx.fillStyle = args.fillStyle;
        ctx.fillRect(0, 0, mod.width, mod.height);   
    }
    
    function _drawText(args)
    {
        ctx.fillStyle = args.fillStyle;
        ctx.font = args.font;
        ctx.fillText(args.text, args.x, args.y);
    }

    function _drawRect(args)
    {
        ctx.lineWidth = args.lineWidth;
        ctx.strokeStyle = args.strokeStyle;
        ctx.beginPath();
        ctx.rect(args.x, args.y, args.width, args.height);
        ctx.stroke();        
    }
    
    function _fillRect(args)
    {
        ctx.fillStyle = args.fillStyle;
        ctx.fillRect(args.x, args.y, args.width, args.height);
    }
    
    function _keyUpListener(e)
    {
        _keysUp[e.key] = true;    
        delete(_keysDown[e.key]); 
    }
    
    function _keyDownListener(e)
    {
        _keysDown[e.key] = true;        
        delete(_keysUp[e.key]);         
    }
    
    mod.isKeyPressed = new Sk.builtin.func((key) => {
        return new Sk.builtin.bool(key in _keysDown);
    });
    
    mod.isKeyReleased = new Sk.builtin.func((key) => {
        var released = key in _keysUp;        
        if (released)
        {
            delete(_keysUp[key]);     
        }                
        return new Sk.builtin.bool(released);
    });
    
    mod.refresh = new Sk.builtin.func(() => {        
        // clean out the whole the commands queue
        _activeCommands = [..._commands];        
        _commands = [];
    });
    
    function getColour(color, defaultCol)
    {
        var rgba;
        
        if (typeof(defaultCol) === 'undefined')
        {
            defaultCol = mod.WHITE;
        }
        
        if (typeof(color) === 'undefined')
        {
            rgba = colours[defaultCol];
        }
        else if (color in colours)
        {
            rgba = colours[color];
        }
        else if (typeof (color) === "string") {
            rgba = color;
        }
        else {
            rgba = "rgba(" + color + "," + g + "," + b + "," + a + ")";
        }            
        return rgba;
    }
        
    
    // Add the say function to the module
    mod.clearScreen = new Sk.builtin.func((color, g , b, a) => {        
        // if you're gonna be clearing the screen
        // clean out the whole the commands queue (to avoid flicker due to drawing multiple screens per frame)
        _activeCommands = [..._commands];
        
        _commands = [];
        
        args = {};
        
        args.fillStyle = getColour(color, mod.BLACK);

        _commands.push([_clearScreen, args]);
        return new Sk.builtin.none;
    });
       
    mod.drawText = new Sk.builtin.func((text, x, y, font, color, g , b, a) => {        
        args = {};
        
        args.font = "32px Consolas";
        if (typeof (font) === "string") 
        {
            args.font = font;
        }             
        
        args.fillStyle = getColour(color);
        
        args.text = text;
        args.x = x;
        args.y = y;
        args.font = font;
        
        _commands.push([_drawText, args]);
        
        return new Sk.builtin.none;        
    });
    
    mod.drawRect = new Sk.builtin.func((x, y, width, height, lineWidth, color, g , b, a) => {
        args = {};
                
        if (typeof(lineWidth) === 'undefined')
        {
            args.lineWidth = "1";
        }
        else
        {
            args.lineWidth = lineWidth;
        }
        args.strokeStyle = getColour(color);
        
        args.x = x;
        args.y = y;
        args.width = width;
        args.height = height;
        
        _commands.push([_drawRect, args]);

        return new Sk.builtin.none;
    });    
    
    mod.fillRect = new Sk.builtin.func((x, y, width, height, color, g , b, a) => {   
        args = {};
        
        args.fillStyle = getColour(color);
        
        args.x = x;
        args.y = y;
        args.width = width;
        args.height = height;

        _commands.push([_fillRect, args]);

        return new Sk.builtin.none;
    });     
 
    return mod;
}