from flask import Flask, render_template, request, jsonify
import ipaddress
import math

app = Flask(__name__)

def calcular_subredes(ip_str, mascara_str, num_subredes, decimal):
    try:
        ip = ipaddress.IPv4Network(ip_str + '/' + mascara_str, strict=False)

        # Calcular la mínima potencia de dos mayor o igual al número de subredes
        potencia_subredes = 2 ** math.ceil(math.log2(num_subredes))

        nuevo_prefijo = ip.prefixlen + math.ceil(math.log2(potencia_subredes))

        if nuevo_prefijo <= 32:
            subredes = list(ip.subnets(new_prefix=nuevo_prefijo))

            info_subredes = []
            for i, subnet in enumerate(subredes):
                primera_direccion_host = subnet.network_address + 1
                ultima_direccion_host = subnet.broadcast_address - 1

                if decimal:
                    info_subred_decimal = {
                        'Numero': i + 1,
                        'Máscara': str(subnet.netmask),
                        'Dirección de Red': str(subnet.network_address),
                        'Primera Dirección de Host': str(primera_direccion_host),
                        'Última Dirección de Host': str(ultima_direccion_host),
                        'Broadcast': str(subnet.broadcast_address)
                    }
                else:
                    info_subred_decimal = {
                        'Numero': i + 1,
                        'Máscara': ip_to_binary(subnet.netmask),
                        'Dirección de Red': ip_to_binary(subnet.network_address),
                        'Primera Dirección de Host': ip_to_binary(primera_direccion_host),
                        'Última Dirección de Host': ip_to_binary(ultima_direccion_host),
                        'Broadcast': ip_to_binary(subnet.broadcast_address)
                    }
                info_subredes.append(info_subred_decimal)

            return info_subredes
        else:
            return None
    except ValueError:
        return None

def ip_to_binary(ip):
    return '.'.join(format(int(octet), '08b') for octet in str(ip).split('.'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/calcular', methods=['POST'])
def calcular():
    ip = request.form['ip']
    mascara = request.form['mascara']
    num_subredes = int(request.form['num_subredes'])

    red = [ip, mascara, num_subredes]
    subredes = calcular_subredes(ip, mascara, num_subredes, True)

    if subredes:
        return render_template('resultados.html', red=red, subredes=subredes)
    else:
        mensaje_error = f"No se pueden calcular {num_subredes} subredes con la máscara {mascara} de la dirección IP {ip}."
        return render_template('error.html', error=mensaje_error)

@app.route('/update_format', methods=['POST'])
def update_format():
    data = request.get_json()
    ip = data['ip']
    mascara = data['mascara']
    num_subredes = int(data['num_subredes'])
    decimal = data['decimal']

    subredes = calcular_subredes(ip, mascara, num_subredes, decimal)

    if subredes:
        return jsonify({'subredes': subredes})
    else:
        mensaje_error = f"No se pueden calcular {num_subredes} subredes con la máscara {mascara} de la dirección IP {ip}."
        return jsonify({'error': mensaje_error}), 400

if __name__ == '__main__':
    app.run(debug=True)
