
async function SendPython(data){
    // Get the reciever endpoint from Python using fetch:
    fetch("http://127.0.0.1:5000/receiver", 
        {
            method: 'POST',
            headers: {
                'Content-type': 'application/json',
                'Accept': 'application/json'
            },
        // Strigify the payload into JSON:
        body:JSON.stringify(data)}).then(res=>res.json()).then(jsonResponse=>{
                
                var possibleMoves = game.moves()
				
                console.log(jsonResponse)
				game.move(jsonResponse)
				board.position(game.fen())
				
            } 
            ).catch((err) => console.error(err));
            		
   }
		   
