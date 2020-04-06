import urllib
import json

data = urllib.urlopen("https://tomc.web.cern.ch/tomc/heavyNeutrino/availableHeavyNeutrinoSamples.txt")
print(data)

masses = []
couplings = []
xsecs = []
xsecs_plus = []
xsecs_minus = []
xsec_dict = {}

lines = []
for line in data:
    if "_mu_" not in line or"dirac" not in line or "HeavyNeutrino" not in line or "lljj" not in line or "Moriond17_aug2018" not in line:
        continue
    if "cc" in line:
        continue
    "- type mass coupling ctau ctauratio events xsec +- xsec+ xsec- "
    lines.append(line)

for line in lines:
    infos = line.split()
    mass = int(float(infos[2]))
    xsec_dict[mass] = []

for line in lines:
    infos = line.split()
    mass = int(float(infos[2]))
    coupling = float(infos[3])
    print(mass,coupling)
    xsec, xsec_up, xsec_down = float(infos[7]), float(infos[9]), float(infos[9]) 
    xsecs = {"xsec": xsec, "xsec_up": xsec_up, "xsec_down": xsec_down}
    xsec_dict[mass].extend([{coupling:xsecs}])

with open('xsec.json', 'w') as f:
        json.dump(xsec_dict, f)

