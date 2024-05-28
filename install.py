import paramiko
import time

# Configuration
host = '192.168.1.99' #Remplacer par l'adresse du Firewall
port = 22
username = 'admin' #Compte par défaut
new_password = 'password'  # Remplacer par le mot de passe souhaité
file_commands = '/home/user/Documents/scripts/commands.txt' #Chemin du fichier contenant les commandes Fortigate à exécuter

# Connexion SSH
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print("Connecting to the host...")

try:
    client.connect(host, port, username=username, password='', allow_agent=False, look_for_keys=False)
    print("Connected to the host.")

    # Ouvrir une session interactive
    ssh_shell = client.invoke_shell()
    print("Interactive shell opened.")

    # Fonction pour attendre une invite spécifique
    def wait_for_prompt(shell, prompt, timeout=30):
        buff = ''
        start_time = time.time()
        while True:
            if time.time() - start_time > timeout:
                raise Exception(f"Timeout waiting for prompt: {prompt}")
            if shell.recv_ready():
                resp = shell.recv(1024)
                buff += resp.decode('utf-8')
                if prompt in buff:
                    print(f"Prompt '{prompt}' found.")
                    break
            time.sleep(0.5)
        return buff

    try:
        # Attendre l'invite pour "New Password"
        print("Waiting for 'New Password:' prompt...")
        wait_for_prompt(ssh_shell, "New Password:")

        # Envoyer le nouveau mot de passe
        print("Sending new password...")
        ssh_shell.send(new_password + '\n')

        # Attendre l'invite pour "Confirm Password"
        print("Waiting for 'Confirm Password:' prompt...")
        wait_for_prompt(ssh_shell, "Confirm Password:")

        # Envoyer le nouveau mot de passe à nouveau pour confirmation
        print("Confirming new password...")
        ssh_shell.send(new_password + '\n')

        # Attendre la confirmation que le mot de passe a été changé
        print("Waiting for final confirmation prompt...")
        output = wait_for_prompt(ssh_shell, "#")
        print("Password changed successfully.")
        print(output)

# Exécuter des commandes supplémentaires sur le Fortigate
        def execute_command(shell, command):
            print(f"Executing command: {command}")
            shell.send(command + '\n')
            time.sleep(1)  # Attendre un peu pour que la commande s'exécute
            output = ''
            while shell.recv_ready():
                output += shell.recv(1024).decode('utf-8')
            print(output)
            return output

	# Lire un fichier de commandes
    with open(commands_file, 'r') as file:
        commands = file.readlines()

    for cmd in commands:
        cmd = cmd.strip()  # Supprimer les espaces en début et fin de ligne
        if cmd and not cmd.startswith('#'):  # Ignorer les lignes vides et les commentaires
            execute_command(ssh_shell, cmd)

        # Commandes à exécuter
#        commands = [
#            'config system interface',  # Commande pour montrer les interfaces du système
#            'edit vlan_lan',
#            'set type vlan',
#            'set vlanid 10',
#            'set interface lan',
#            'set ip 10.20.30.40/24',
#            'set vdom root',
#            'next',
#            'end',
#            'exit',
            # Ajoute d'autres commandes ici
#        ]

#        for cmd in commands:
#            execute_command(ssh_shell, cmd)
#       scp firmware.out -J 192.168.1.99 $username:$new_password
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Fermer la connexion
        client.close()
        print("Connection closed.")
except Exception as e:
    print(f"Connection failed: {e}")
