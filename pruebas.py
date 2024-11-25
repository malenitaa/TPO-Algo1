#PRUEBAS    
def test_validar_fecha():
    hoy = datetime.now().date()
    fecha_valida = "12/25/24"  # Fecha futura (es formato mm/dd/aa)
    fecha_invalida = "01/01/23"  # Fecha pasada

    # Validar fecha válida
    fecha_turno = datetime.strptime(fecha_valida, "%m/%d/%y").date()
    assert fecha_turno >= hoy

    # Validar fecha inválida
    fecha_turno_invalida = datetime.strptime(fecha_invalida, "%m/%d/%y").date()
    assert fecha_turno_invalida < hoy

def test_validar_nombre():
    with pytest.raises(ValueError):
        validar_nombre("Juan", None)  # Nombre sin apellido

    with pytest.raises(ValueError):
        validar_nombre("1234", None)  # Nombre con caracteres no válidos

    assert validar_nombre("Juan Pérez", None) is None  # Nombre correcto

def test_validate_phone():
    assert validate_phone("+541112345678", None)  # Número válido
    assert not validate_phone("+5412345678", None)  # Número muy corto
    assert not validate_phone("112345678", None)  # Número sin prefijo