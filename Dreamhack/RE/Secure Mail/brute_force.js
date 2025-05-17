for(var year = 0; year<100; year++){
    var result = 0;
    for(var month=1; month<13; month++){
        for(var day=1; day<32; day++){
            var pw = String(year).padStart(2,'0') + String(month).padStart(2,'0') + String(day).padStart(2,'0');
            result = _0x9a220(pw);
            if(result){
                break;
            }
        }
        if(result){
            break;
        }
    }
    if(result){
        break;
    }
}
