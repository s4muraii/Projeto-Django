from rolepermissions.roles import AbstractUserRole

class secretaria(AbstractUserRole):
    available_permissions = {
    'cadastrar_funcionario': True,
    'deletar_horario': True,
    
    }

class funcionario(AbstractUserRole):
    available_permissions = {
    'cadastrar_horario': True,
    'deletar_horario': False,
    'Ver_horarios': True,
    }
