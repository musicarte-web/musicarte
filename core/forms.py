from django import forms

from .models import (
    Aluno,
    Instrutor,
    Curso,
    Matricula,
    Aula,
    Evento,
    Midia,
)


class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


# =========================================================
# FORMULÁRIO PÚBLICO DE INSCRIÇÃO
# =========================================================

class InscricaoOficinaForm(forms.Form):
    nome = forms.CharField(
        max_length=120,
        label="Nome completo",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Digite seu nome completo",
            }
        ),
    )

    idade = forms.IntegerField(
        min_value=1,
        max_value=120,
        label="Idade",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "Sua idade",
            }
        ),
    )

    telefone = forms.CharField(
        max_length=30,
        label="Telefone",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "(44) 99999-9999",
            }
        ),
    )

    email = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "seuemail@exemplo.com",
            }
        ),
    )


# =========================================================
# FORMULÁRIOS ADMINISTRATIVOS
# =========================================================

class AlunoForm(StyledModelForm):
    class Meta:
        model = Aluno
        fields = ["nome", "idade", "telefone", "email"]


class InstrutorForm(StyledModelForm):
    class Meta:
        model = Instrutor
        fields = [
            "nome",
            "especialidade",
            "telefone",
            "email",
            "foto",
            "ativo",
        ]


class CursoForm(StyledModelForm):
    class Meta:
        model = Curso
        fields = [
            "nome",
            "descricao",
            "carga_horaria",
            "instrutor",
            "horario",
            "local",
            "vagas",
            "imagem",
            "ativo",
        ]


class MatriculaForm(StyledModelForm):
    class Meta:
        model = Matricula
        fields = [
            "aluno",
            "curso",
            "status",
        ]


class AulaForm(StyledModelForm):
    class Meta:
        model = Aula
        fields = [
            "curso",
            "tema",
            "data",
            "observacoes",
        ]

        widgets = {
            "data": forms.DateInput(
                attrs={"type": "date"}
            )
        }


class EventoForm(StyledModelForm):
    class Meta:
        model = Evento
        fields = [
            "titulo",
            "descricao",
            "data",
            "horario",
            "local",
            "imagem",
            "publicado",
        ]

        widgets = {
            "data": forms.DateInput(
                attrs={"type": "date"}
            ),
            "horario": forms.TimeInput(
                attrs={"type": "time"}
            ),
        }


class MidiaForm(StyledModelForm):
    class Meta:
        model = Midia
        fields = [
            "titulo",
            "imagem",
            "legenda",
            "data",
            "publicada",
        ]

        widgets = {
            "data": forms.DateInput(
                attrs={"type": "date"}
            )
        }