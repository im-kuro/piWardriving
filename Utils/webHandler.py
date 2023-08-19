from sanic import Sanic
from sanic.response import json, html
import platform,socket,re,uuid,psutil,subprocess, pywifi
from jinja2 import Environment, FileSystemLoader
import tools



app = Sanic("WardrivingTool")
app.static('Utils/static/', 'Utils/static/', directory_view=True, name="static")  # Assuming your static files are in a 'static' folder

# Configure Jinja2 template environment
template_dir = 'Utils/static/'  # Path to your template directory
env = Environment(loader=FileSystemLoader(template_dir))

app.ctx.interfaces = tools.toolkit.showInterfaces()
app.ctx.interface = None
"""

FRONT END CODE HERE

"""


    
    
@app.route("/")
async def index(request):
    template = env.get_template('index.html')

    rendered_template = template.render(deviceInfo={
        "machineType": platform.machine(),
        "os": platform.system(),
        "mac": ':'.join(re.findall('..', '%012x' % uuid.getnode())).upper,
        "ram": str(round(psutil.virtual_memory().total / (1024.0 **3)))+" GB",
        "ip": socket.gethostbyname(socket.gethostname()),
        "hostname": socket.gethostname(),
        "interfaces": app.ctx.interfaces,
        "chosenInterface": app.ctx.interface,
        "chosenInterfaceName": app.ctx.interface if app.ctx.interface is not None else None

    })
    
    return html(rendered_template)


@app.route("/analytics", methods=["GET"])
async def analytics(request):
    template = env.get_template('analytics.html')
    rendered_template = template.render(deviceInfo={
        
    })
    return html(rendered_template)


@app.route("/output", methods=["GET"])
async def output(request):
    template = env.get_template('output.html')
    rendered_template = template.render(deviceInfo={
        
    })
    return html(rendered_template)


"""
BACK END CODE HERE
"""


# gets called when user enters site and gets the interface
@app.route('/setInterface', methods=["POST"])
async def setInterface(request):
    app.ctx.interface = request.json["interfaceIdx"]
    tools.toolkit.__init__(app.ctx.interface)
    return json({"status": "success", "interface": app.ctx.interface})



@app.route('/startWardriving', methods=["GET"])
async def startWardrive(request):
    return json({'status': "success", "results": "cum"})


@app.route('/data', methods=["GET"])
async def getData(request):
    return json({'temperature': tools.toolkit.get_cpu_temperature(), 'cpuUsage': tools.toolkit.get_cpu_usage()})



@app.route('/networks', methods=['GET'])
async def get_networks(request):
    
    networkRes = await tools.toolkit.scan_wifi_networks(app.ctx.interface)
    
    if networkRes is None:
        return json({"status": "error", "message": "No interface selected"})
    
    WPANetworks = 0
    WPA2Networks = 0
    WPA3Networks = 0
    WEPNetworks = 0
    networkCount = 0
    for network_info in networkRes.values():
        networkCount += 1
        encryption_type = network_info["encryption"][0]  # Assuming the encryption type is a single integer
        
        if encryption_type == 4:
            WPA2Networks += 1
        elif encryption_type == 5:
            WPA3Networks += 1
        elif encryption_type == 2 or encryption_type == 3:
            WPANetworks += 1
        elif encryption_type == 1:
            WEPNetworks += 1


    return json({
        "networks": networkRes,
        "networkCount": networkCount,
        "WPA": WPANetworks,
        "WPA2": WPA2Networks,
        "WPA3": WPA3Networks,
        "WEP": WEPNetworks
    })



if __name__ == "__main__":
    app.run(host="127.0.0.1", port=6969)
