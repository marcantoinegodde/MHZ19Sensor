#Import bibliothèques
import datetime
import time
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from pmsensor import co2sensor

########## Définition des fonctions ##########

#Affichage + logging
def output(time, concentration, temperature):
    print("{}: {} ppm - {} °C".format(time, concentration, temperature))
    with open(output_file, 'a') as file:
        print("{},{},{}".format(time, concentration, temperature), file=file)

#Lecture capteur
def get_co2_and_temp():
    i = 1
    start = datetime.datetime.now()
    t = 0
    while t < args.max_time:

        #Trigger intervalle
        while True:
            now = datetime.datetime.now()
            t = (now - start).total_seconds()
            if t > i * args.interval:
                break
            time.sleep(0.05)

        i += 1

        co2, temp = co2sensor.read_mh_z19_with_temperature(args.port) #Lecture capteur
        output(now, co2, temp) #Logging
        yield co2, temp, t

#Création du graphe matplotlib
def init_anim():
    global fig, ax_co2, ax_temp, ln_co2, ln_temp

    fig, ax_co2 = plt.subplots()
    ax_temp = ax_co2.twinx()
    ln_co2, = ax_co2.plot(data_time, data_co2, animated=True, color="red", label="CO2 (ppm)", linestyle='', marker='.')
    ln_temp, = ax_temp.plot(data_time, data_temp, animated=True, color="green", label="Température (°C)", linestyle='', marker='*')
    ax_co2.set_xlabel("temps (s)")
    ax_co2.set_ylabel("ppm")
    ax_co2.legend(loc='upper left')
    ax_temp.set_ylabel("°C")
    ax_temp.legend(loc='upper right')
    ax_co2.set_xlim(0, args.max_time)
    ax_co2.set_ylim(0, 5000)
    ax_temp.set_ylim(0, 50)
    plt.title("Evolution de la concentration de CO2 et de la température\nen fonction du temps ({})".format(datetime.datetime.now()))

#Mise à jour du graphe
def update_anim(frames):
    co2, temp, t = frames

    data_temp.append(temp)
    data_co2.append(co2)
    data_time.append(t)

    ln_co2.set_data(data_time, data_co2)
    ln_temp.set_data(data_time, data_temp)

    return ln_co2, ln_temp

########## Début du script ##########

#Arguments du script
parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter) #Définition des arguments du script
parser.add_argument("-o", "--output-csv", default="co2.csv", help="Fichier de destination des données")
parser.add_argument("-f", "--output-image", default="co2.png", help="Fichier de destinaton du graphique")
parser.add_argument("-i", "--interval", default=2, type=float, help="Intervalle de mesure (secondes)")
parser.add_argument("-p", "--port", default="/dev/serial0", help="Port du capteur")
parser.add_argument("-t", "--max-time", default=600.0, type=float, help="Durée mesures (secondes)")
args = parser.parse_args()

output_file = args.output_csv #Définition du fichier export

print("Écriture dans {}". format(output_file))

#Définition listes valeur
data_co2 = []
data_temp = []
data_time = []

init_anim()

ani = FuncAnimation(fig, update_anim, frames=get_co2_and_temp, blit=True, repeat=False) #Mise à jour de l'animation
plt.show()

fig.savefig(args.output_image) #Enregistrement du graphe
print("Graphique enregistré dans {}".format(args.output_image))
