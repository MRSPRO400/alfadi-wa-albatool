function countdown(){
    let seconds = document.getElementById("seconds");
    let minutes = document.getElementById("minutes");

    setInterval(()=>{
        let sec = parseInt(seconds.innerText);
        sec--;

        if(sec < 0){
            sec = 59;
        }

        seconds.innerText = sec < 10 ? "0"+sec : sec;
    },1000);
}

countdown();