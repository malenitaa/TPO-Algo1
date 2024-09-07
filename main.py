import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
import secrets
import json
import os
from twilio.rest import Client

#Twilio
ACCOUNT_SID = 'AC2a5e1f0b785cbef8d46cd60143678688'
AUTH_TOKEN = '97423e9dcbda897368147000870e79a1'
TWILIO_PHONE = '+5491156090716'

client = Client(ACCOUNT_SID, AUTH_TOKEN)

users_file = 'data/users.json'

def load_users():
    if os.path.exists(users_file):
        with open(users_file, 'r') as file:
            return json.load(file)
    else:
        return []

def save_users(users):
    with open(users_file, 'w') as file:
        json.dump(users, file, indent=4)

def format_phone(phone):
    """ Asegúrate de que el número tenga el prefijo internacional correcto y no tenga un '11' de más. """
    phone = phone.strip()  # Elimina espacios en blanco
    if phone.startswith("11"):
        phone = phone[2:]  # Elimina el "11" si está al principio
    if not phone.startswith("+"):
        phone = "+549" + phone  # Agrega el prefijo de Argentina si no está
    return phone

def send_code(phone, code):
    formatted_phone = format_phone(phone)
    message = f"Su código de verificación es: {code}"
    try:
        response = client.messages.create(
            body=message,
            from_=TWILIO_PHONE,
            to=formatted_phone
        )
        print(f'Código enviado a {formatted_phone}. SID del mensaje: {response.sid}')
    except Exception as e:
        print(f'Error al enviar SMS: {e}')

#generar código
def generate_and_send_code(full_name, phone):
    code = secrets.token_hex(3)  
    users = load_users()

    existing_user = next((u for u in users if u["phone"] == phone), None)

    if existing_user:
        send_code(phone, code)
    else:
        new_user = {
            "id": len(users) + 1,
            "category": "Patient",
            "name": full_name,
            "phone": phone
        }
        users.append(new_user)
        save_users(users)
        send_code(phone, code)

    return code

#app
def login_screen():
    top = tk.Toplevel(root)
    top.title("Iniciar Sesión")

    def verify_user():
        full_name = full_name_entry.get()
        phone = phone_entry.get()
        if full_name and phone:
            generated_code = generate_and_send_code(full_name, phone)
            print(f'Código generado: {generated_code}')
            verify_code_screen(phone, generated_code)
        else:
            print("Por favor ingrese nombre y celular.")

    mainframe = ttk.Frame(top, padding="10 10 20 20")
    mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

    full_name_entry = ttk.Entry(mainframe, width=30)
    full_name_entry.grid(column=1, row=1, padx=5, pady=5)
    ttk.Label(mainframe, text="Nombre Completo:").grid(column=0, row=1, padx=5, pady=5)

    phone_entry = ttk.Entry(mainframe, width=30)
    phone_entry.grid(column=1, row=2, padx=5, pady=5)
    ttk.Label(mainframe, text="Teléfono Celular:").grid(column=0, row=2, padx=5, pady=5)
    
    ttk.Button(mainframe, text="Enviar Código", command=verify_user).grid(column=1, row=3, padx=5, pady=5)

#verificador
def verify_code_screen(phone, generated_code):
    def check_code():
        entered_code = code_entry.get()
        if entered_code == generated_code:
            print("Código Correcto")
            users = load_users()
            user_data = next((u for u in users if u["phone"] == phone), None)
            if user_data:
                if user_data["category"] == "Doctor":
                    doctor_screen()
                else:
                    patient_screen()
        else:
            print("Código Incorrecto")

    top_code = tk.Toplevel(root)
    top_code.title("Validar Código")

    mainframe = ttk.Frame(top_code, padding="10 10 20 20")
    mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

    code_entry = ttk.Entry(mainframe, width=10)
    code_entry.grid(column=1, row=1, padx=5, pady=5)
    ttk.Label(mainframe, text="Código:").grid(column=0, row=1, padx=5, pady=5)
    
    ttk.Button(mainframe, text="Verificar", command=check_code).grid(column=1, row=2, padx=5, pady=5)

#pantalla doctor
def doctor_screen():
    top_doctor = tk.Toplevel(root)
    top_doctor.title("Doctor")
    
    cal = Calendar(top_doctor, selectmode='day', year=2024, month=9, day=7)
    cal.pack(pady=20)
    
    #mensajes
    mensaje_box = tk.Text(top_doctor, height=5, width=40)
    mensaje_box.pack(pady=10)

    def enviar_mensaje():
        mensaje = mensaje_box.get("1.0", tk.END).strip()
        if mensaje:
            users = load_users()
            for user in users:
                send_code(user['phone'], mensaje)  #Twilio
            print(f"Mensaje enviado a todos los usuarios: {mensaje}")
        else:
            print("El mensaje está vacío.")

    ttk.Button(top_doctor, text="Enviar Mensaje a Usuarios", command=enviar_mensaje).pack(pady=10)


#pantalla paciente
def patient_screen():
    top_patient = tk.Toplevel(root)
    top_patient.title("Paciente")
    
    cal = Calendar(top_patient, selectmode='day', year=2024, month=9, day=7)
    cal.pack(pady=20)

    def reservar_turno():
        fecha_seleccionada = cal.get_date()
        print(f"Turno reservado para: {fecha_seleccionada}")

    ttk.Button(top_patient, text="Reservar Turno", command=reservar_turno).pack(pady=10)
    
    def ver_turnos_anteriores():
        print("Mostrando turnos anteriores")

    ttk.Button(top_patient, text="Turnos Anteriores", command=ver_turnos_anteriores).pack(pady=10)


#llamada a main
root = tk.Tk()
root.title("Consultorio")

ttk.Button(root, text="Iniciar Sesión/Registrarse", command=login_screen).pack(padx=10, pady=10)

root.mainloop()
