import datetime
import time
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from pmsensor import co2sensor

def output(time, concentration, temperature):
    print("{}: {} ppm - {} °C".format(time, concentration, temperature))
    with open(output_file, 'a') as file:
        print("{},{},{}".format(time, concentration, temperature), file=file)

def get_co2_and_temp():
    i = 1
    start = datetime.datetime.now()
    t = 0
    while t < args.max_time:
        while True:
            now = datetime.datetime.now()
            t = (now - start).total_seconds()
            if t > i * args.interval:
                break
            time.sleep(0.05)

        i += 1

        if args.debug:
            co2, temp = 1500 + i, 15 + i
        else:
            co2, temp = co2sensor.read_mh_z19_with_temperature(args.port)
        output(now, co2, temp)
        yield co2, temp, t

def init_anim():
    global fig, ax_co2, ax_temp, ln_co2, ln_temp
    fig, ax_co2 = plt.subplots()
    ax_temp = ax_co2.twinx()
    ln_co2, = ax_co2.plot(data_time, data_co2, 'ro', animated=True, color="red", label="CO2 (ppm)", linestyle=args.line_style, marker='.')
    ln_temp, = ax_temp.plot(data_time, data_temp, 'ro', animated=True, color="green", label="Température (°C)", linestyle=args.line_style, marker='*')
    ax_co2.set_xlabel("temps (s)")
    ax_co2.set_ylabel("ppm")
    ax_co2.legend(loc='upper left')
    ax_temp.set_ylabel("°C")
    ax_temp.legend(loc='upper right')

    ax_co2.set_xlim(0, args.max_time)
    ax_co2.set_ylim(0, 5000)
    ax_temp.set_ylim(0, 50)
    plt.title("Evolution de la concentration de CO2 et de la température\n ({})".format(datetime.datetime.now()))

def update_anim(frames):
    co2, temp, t = frames

    data_temp.append(temp)
    data_co2.append(co2)
    data_time.append(t)

    ln_co2.set_data(data_time, data_co2)
    ln_temp.set_data(data_time, data_temp)

    return ln_co2, ln_temp

parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument("-o", "--output-csv", help="Fichier de destination", default="co2.csv")
parser.add_argument("-f", "--output-image", default="co2.png", help="Fichier de destinaton de l'image du graphique")
parser.add_argument("-i", "--interval", type=float, help="Intervalle de mesure, en secondes", default=2)
parser.add_argument("-p", "--port", default="/dev/serial0", help="Le port de connexion à la sonde")
parser.add_argument("-d", "--debug", default=False, action="store_true", help="Ne pas lire les données de la sonde et utiliser des valeurs factices.")
parser.add_argument("-l", "--line-style", default='', help="Le style de la lingne affichée peut être '', :', '-', '--' ou '-.'")
parser.add_argument("-t", "--max-time", default=600.0, type=float, help="Le maximum initial sur l'axe des abscisses")
args = parser.parse_args()

output_file = args.output_csv

print("On écrit dans {}". format(output_file))

# mesure qui ne sert a rien
if args.debug:
    co2, temp = 1500, 10
else:
    co2, temp = co2sensor.read_mh_z19_with_temperature(args.port)

data_co2 = []
data_temp = []
data_time = []
init_anim()

print("Appuyez sur CTRL+C pour quitter")
ani = FuncAnimation(fig, update_anim, frames=get_co2_and_temp, blit=True, repeat=False)
plt.show()

fig.savefig(args.output_image)
print("Graphique enregistré dans {}".format(args.output_image))
