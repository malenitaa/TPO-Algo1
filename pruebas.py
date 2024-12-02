from unittest.mock import Mock
import pytest
from main import validar_nombre, validar_telefono, formatear_nombre

def test_validar_nombre_invalido():
    mock_error_label = Mock()
    
    # Caso: solo nombre (sin apellido)
    with pytest.raises(ValueError):
        validar_nombre("Malena", mock_error_label)
    
    # Caso: nombre con caracteres no alfabéticos
    with pytest.raises(ValueError):
        validar_nombre("Malena123", mock_error_label)
    
    mock_error_label.configure.assert_any_call(
        text="Por favor ingrese un nombre completo (nombre y apellido).", text_color="red"
    )
    
    mock_error_label.configure.assert_any_call(
        text="El nombre completo solo debe contener letras y espacios.", text_color="red"
    )

def test_formatear_nombre():
    # Prueba con nombre con tildes
    nombre = "José Maria"
    assert formatear_nombre(nombre) == "Jose Maria"
    
    # Prueba con nombre sin tildes
    nombre = "malena"
    assert formatear_nombre(nombre) == "Malena"
    
    # Prueba con nombre con otros caracteres
    nombre = "mARÍA jose"
    assert formatear_nombre(nombre) == "Maria Jose"


def test_validar_telefono():
    mock_error_label = Mock()
    # Prueba con un número válido
    assert validar_telefono("+541112345678", mock_error_label)
    # Prueba con un número corto 
    with pytest.raises(ValueError):
        validar_telefono("+5412345678", mock_error_label)
    mock_error_label.configure.assert_called_with(
        text="Por favor ingrese el número en el formato '+54' seguido de 10 dígitos sin el prefijo '9'.", 
        text_color="red")
