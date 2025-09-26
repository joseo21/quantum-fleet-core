"""
Utilidades de seguridad para la plataforma.

Incluye:
- Hashing y verificación de contraseñas usando Passlib/bcrypt.
- Validación de política de contraseñas (configurable).
- Generación de API keys / tokens cripto-seguros para dispositivos u otros usos.

Este módulo es autocontenido y seguro de usar en producción.
"""

from __future__ import annotations

from dataclasses import dataclass
from secrets import token_urlsafe
from typing import List, Tuple

from passlib.context import CryptContext

# Contexto de hashing con bcrypt (recomendado por OWASP para credenciales)
_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Genera el hash seguro de una contraseña en texto plano.

    Args:
        password: Contraseña del usuario en texto plano.

    Returns:
        Hash irreversible (con salt) apto para almacenar en DB.
    """
    if not isinstance(password, str) or password == "":
        raise ValueError("La contraseña no puede estar vacía.")
    return _pwd_ctx.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verifica si la contraseña en texto plano coincide con el hash almacenado.

    Args:
        password: Contraseña en texto plano.
        password_hash: Hash almacenado.

    Returns:
        True si coincide, False en caso contrario.
    """
    if not password_hash:
        return False
    try:
        return _pwd_ctx.verify(password, password_hash)
    except Exception:
        # Si el hash es inválido/corrupto, mejor devolver False que propagar detalles
        return False


@dataclass(frozen=True)
class PasswordPolicy:
    """
    Política de contraseñas a nivel de plataforma (ajústala si lo necesitas).

    Atributos:
        min_length: Largo mínimo.
        require_upper: Al menos una mayúscula A-Z.
        require_lower: Al menos una minúscula a-z.
        require_digit: Al menos un dígito 0-9.
        require_special: Al menos un carácter especial.
        special_chars: Conjunto aceptado de caracteres especiales.
    """
    min_length: int = 10
    require_upper: bool = True
    require_lower: bool = True
    require_digit: bool = True
    require_special: bool = True
    special_chars: str = "!@#$%^&*()-_=+[]{};:,.?/\\|`~"

    def check(self, password: str) -> Tuple[bool, List[str]]:
        """
        Valida una contraseña según esta política.

        Returns:
            (ok, errores) donde ok es True si cumple, y errores
            contiene mensajes en caso de incumplimiento.
        """
        errors: List[str] = []
        if not isinstance(password, str) or len(password) < self.min_length:
            errors.append(f"Debe tener al menos {self.min_length} caracteres.")
        if self.require_upper and not any(c.isupper() for c in password):
            errors.append("Debe contener al menos una letra mayúscula (A-Z).")
        if self.require_lower and not any(c.islower() for c in password):
            errors.append("Debe contener al menos una letra minúscula (a-z).")
        if self.require_digit and not any(c.isdigit() for c in password):
            errors.append("Debe contener al menos un número (0-9).")
        if self.require_special and not any(c in self.special_chars for c in password):
            errors.append("Debe contener al menos un carácter especial.")
        return (len(errors) == 0, errors)


# Política por defecto (puedes cambiarla en registro/reset si lo deseas)
DEFAULT_PASSWORD_POLICY = PasswordPolicy()


def check_password_policy_or_raise(password: str, policy: PasswordPolicy = DEFAULT_PASSWORD_POLICY) -> None:
    """
    Lanza ValueError con mensajes claros si la contraseña NO cumple la política.

    Útil para usar en el endpoint de registro o cambio de contraseña.
    """
    ok, errs = policy.check(password)
    if not ok:
        raise ValueError("Contraseña insegura: " + " ".join(errs))


def generate_api_key(nbytes: int = 24) -> str:
    """
    Genera una API key / token cripto-seguro URL-safe.

    Args:
        nbytes: Entropía en bytes antes del encoding (24 ≈ 32-33 chars).

    Returns:
        Cadena segura, apta para identificadores de dispositivos u otros usos.
    """
    if nbytes < 16:
        # 16 bytes (~128 bits) es un mínimo razonable para producción
        nbytes = 16
    return token_urlsafe(nbytes)


__all__ = [
    "hash_password",
    "verify_password",
    "PasswordPolicy",
    "DEFAULT_PASSWORD_POLICY",
    "check_password_policy_or_raise",
    "generate_api_key",
]
