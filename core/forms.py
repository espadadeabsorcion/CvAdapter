from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags

from perfil.models import Perfil


class RegistroUsuarioForm(forms.Form):
    """
    Formulario público de auto-registro para nuevos usuarios.
    Crea el User de Django y su Perfil asociado.
    """
    nombre_completo = forms.CharField(
        max_length=100,
        label="Nombre Completo",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej. Ana María Gómez',
            'required': 'required'
        })
    )
    username = forms.CharField(
        max_length=150,
        label="Nombre de Usuario",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej. anagomez',
            'required': 'required',
            'autocomplete': 'username'
        }),
        help_text="Solo letras, números y los caracteres @/./+/-/_."
    )
    email = forms.EmailField(
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'ana@ejemplo.com',
            'required': 'required',
            'autocomplete': 'email'
        })
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mínimo 8 caracteres',
            'required': 'required',
            'autocomplete': 'new-password'
        })
    )
    password_confirm = forms.CharField(
        label="Confirmar Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Repite tu contraseña',
            'required': 'required',
            'autocomplete': 'new-password'
        })
    )

    def clean_nombre_completo(self):
        nombre = self.cleaned_data.get('nombre_completo', '').strip()
        return strip_tags(nombre)

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("Este nombre de usuario ya está registrado.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Este correo electrónico ya está registrado.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('password_confirm')

        if p1 and p2 and p1 != p2:
            self.add_error('password_confirm', 'Las contraseñas no coinciden.')
        elif p1:
            try:
                validate_password(p1)
            except ValidationError as err:
                self.add_error('password', err)

        return cleaned_data

    def save(self) -> User:
        """Crea el User y su Perfil profesional base."""
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['nombre_completo'][:30],
        )
        Perfil.objects.create(
            usuario=user,
            nombre_completo=self.cleaned_data['nombre_completo'],
            email=self.cleaned_data['email'],
            titulo_profesional="Profesional",
            resumen_profesional="Perfil profesional en construcción.",
        )
        return user


class EliminarCuentaPropiaForm(forms.Form):
    """
    Formulario de confirmación para que un usuario autenticado elimine su propia cuenta.
    Requiere ingresar la contraseña actual y marcar la casilla de confirmación.
    """
    password = forms.CharField(
        label="Tu contraseña actual",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu contraseña para confirmar',
            'required': 'required'
        }),
        help_text="Por seguridad, confirma tu contraseña actual."
    )
    confirmacion = forms.BooleanField(
        label="Entiendo que esta acción es permanente y eliminará todos mis datos, CVs y certificados subidos.",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'required': 'required'
        })
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if self.user and not self.user.check_password(password):
            raise ValidationError("La contraseña ingresada es incorrecta.")
        return password


class UsuarioAdminCreateForm(forms.Form):
    """
    Formulario del CRUD Admin para crear un nuevo usuario con permisos y perfil.
    """
    nombre_completo = forms.CharField(
        max_length=100,
        label="Nombre Completo",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Carlos Ruiz'})
    )
    username = forms.CharField(
        max_length=150,
        label="Nombre de Usuario",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'cruiz'})
    )
    email = forms.EmailField(
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'carlos@ejemplo.com'})
    )
    password = forms.CharField(
        label="Contraseña Inicial",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mínimo 8 caracteres'})
    )
    is_staff = forms.BooleanField(
        required=False,
        label="¿Es Administrador (Staff)?",
        help_text="Permite acceder a la administración y gestión de usuarios.",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        label="Cuenta Activa",
        help_text="Desmarcar para suspender el acceso de este usuario.",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def clean_nombre_completo(self):
        return strip_tags(self.cleaned_data.get('nombre_completo', '').strip())

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("Este nombre de usuario ya está en uso.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Este correo ya está registrado con otro usuario.")
        return email

    def clean_password(self):
        p = self.cleaned_data.get('password')
        if p:
            try:
                validate_password(p)
            except ValidationError as err:
                raise err
        return p

    def save(self) -> User:
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['nombre_completo'][:30],
            is_staff=self.cleaned_data.get('is_staff', False),
            is_active=self.cleaned_data.get('is_active', True),
        )
        Perfil.objects.create(
            usuario=user,
            nombre_completo=self.cleaned_data['nombre_completo'],
            email=self.cleaned_data['email'],
            titulo_profesional="Profesional",
            resumen_profesional="Perfil profesional en construcción.",
        )
        return user


class UsuarioAdminUpdateForm(forms.Form):
    """
    Formulario del CRUD Admin para editar datos de usuario, permisos y contraseña opcional.
    """
    nombre_completo = forms.CharField(
        max_length=100,
        label="Nombre Completo",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    username = forms.CharField(
        max_length=150,
        label="Nombre de Usuario",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    new_password = forms.CharField(
        required=False,
        label="Nueva Contraseña (opcional)",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Dejar en blanco para no cambiar'}),
        help_text="Solo llena este campo si deseas cambiar la contraseña del usuario."
    )
    is_staff = forms.BooleanField(
        required=False,
        label="¿Es Administrador (Staff)?",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    is_active = forms.BooleanField(
        required=False,
        label="Cuenta Activa",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def __init__(self, *args, instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = instance
        if instance:
            self.fields['username'].initial = instance.username
            self.fields['email'].initial = instance.email
            self.fields['is_staff'].initial = instance.is_staff
            self.fields['is_active'].initial = instance.is_active
            perfil = getattr(instance, 'perfil', None)
            if perfil:
                self.fields['nombre_completo'].initial = perfil.nombre_completo
            else:
                self.fields['nombre_completo'].initial = instance.get_full_name() or instance.username

    def clean_nombre_completo(self):
        return strip_tags(self.cleaned_data.get('nombre_completo', '').strip())

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        qs = User.objects.filter(username__iexact=username)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Este nombre de usuario ya está en uso.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        qs = User.objects.filter(email__iexact=email)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Este correo ya está registrado con otro usuario.")
        return email

    def clean_new_password(self):
        p = self.cleaned_data.get('new_password')
        if p:
            try:
                validate_password(p, user=self.instance)
            except ValidationError as err:
                raise err
        return p

    def save(self) -> User:
        user = self.instance
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['nombre_completo'][:30]
        user.is_staff = self.cleaned_data.get('is_staff', False)
        user.is_active = self.cleaned_data.get('is_active', True)

        new_password = self.cleaned_data.get('new_password')
        if new_password:
            user.set_password(new_password)

        user.save()

        # Actualizar perfil
        perfil, _ = Perfil.objects.get_or_create(
            usuario=user,
            defaults={
                'nombre_completo': self.cleaned_data['nombre_completo'],
                'email': self.cleaned_data['email'],
                'titulo_profesional': 'Profesional',
                'resumen_profesional': 'Perfil en construcción.',
            }
        )
        perfil.nombre_completo = self.cleaned_data['nombre_completo']
        perfil.email = self.cleaned_data['email']
        perfil.is_active = user.is_active
        perfil.save()

        return user
