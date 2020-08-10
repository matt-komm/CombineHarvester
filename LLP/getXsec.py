import urllib.request
import json
import yaml

data = urllib.request.urlopen("https://tomc.web.cern.ch/tomc/heavyNeutrino/availableHeavyNeutrinoSamples.txt")
mybytes = data.read().decode("utf8")
dataSplit = mybytes.split('\n')


masses = []
couplings = []
xsecs = []
xsecs_plus = []
xsecs_minus = []
xsec_dict = {}
xsec_dict_cc = {}
yaml_dict = {}

lines = []
for line in dataSplit:
    if "_mu_" not in line or "dirac" not in line or "HeavyNeutrino" not in line or "lljj" not in line or "2017" not in line:
        continue
    print(line)
    "- type mass coupling ctau ctauratio events xsec +- xsec+ xsec- "
    lines.append(line)

for line in lines:
    infos = line.split()
    mass = int(float(infos[2]))
    xsec_dict[mass] = []
    xsec_dict_cc[mass] = []

for line in lines:
    name = infos[11].split('/')[-1]
    infos = line.split()
    mass = int(float(infos[2]))
    coupling = float(infos[3])
    print(mass,coupling)
    xsec, xsec_up, xsec_down = float(infos[7]), float(infos[9]), float(infos[9]) 
    xsecs = {"xsec": xsec, "xsec_up": xsec_up, "xsec_down": xsec_down}
    print(name, xsec)
    if "cc" in line:
        xsec_dict_cc[mass].extend([{coupling:xsecs}])
    else:
        xsec_dict[mass].extend([{coupling:xsecs}])
    yaml_dict[name] = xsec


for mass, couplings in xsec_dict.items():
    for i, coupling in enumerate(couplings):
        found = False
        for key in coupling.keys():
            for cc_coupling in xsec_dict_cc[mass]:
                print(key, cc_coupling)
                if key in cc_coupling:
                    print("found", key)
                    found = True
                    xsec_dict[mass][i][key]["xsec"] += cc_coupling[key]["xsec"]
                    xsec_dict[mass][i][key]["xsec_up"] += cc_coupling[key]["xsec_up"]
                    xsec_dict[mass][i][key]["xsec_down"] += cc_coupling[key]["xsec_down"]
        if not found:
            coupling.pop(key)
    filter(None, couplings)

print(xsec_dict)

with open('xsec.json', 'w') as f:
    json.dump(xsec_dict, f)

with open('xsec.yaml', 'w') as f:
    yaml.dump(yaml_dict, f)

