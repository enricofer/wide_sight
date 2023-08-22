<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>wide_sight_frontend</title><style>body {
      display: flex;
      height: 100vh;
      margin: 0;
    }

    #ws1{
      width:1000px;
      height:600px;
      background-color: gray;
    }

    #ws2{
      flex: 1;
      background: tan;
    }

    wide-sight {
      width:100%;
      height:100%;
    }</style><link href=/static/css/app.619e0114a0b14c07af1bbcf3103d3c8c.css rel=stylesheet></head><body onload=connectEvents()><div id=ws2><wide-sight backend=https://beato.duckdns.org:8443 apikey=3788e7c9-ace9-4fb6-95b9-db6170b6286f panokey=6d5e2b70-8517-44a8-acd5-e7c12e00272a overlay=https://beato.duckdns.org:8443/static/test.geo.json></wide-sight></div><script>function connectEvents(){
        const ws_el = document.getElementsByTagName("wide-sight")[0]
        console.log("WS",ws_el)
        ws_el.on('ViewChanged', function(payload){
          console.log('PAYLOAD',payload)
        })
        ws_el.on('click', function(ev){
          console.log('CLICK',ev)
        })
      }</script><script type=text/javascript src=/static/js/manifest.2ae2e69a05c33dfc65f8.js></script><script type=text/javascript src=/static/js/vendor.18290c6ecb5cb5f60821.js></script><script type=text/javascript src=/static/js/app.87c3969cdd0208e6b564.js></script></body></html>