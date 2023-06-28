import openai  # pip install openai
import typer  # pip install "typer[all]"
from rich import print  # pip install rich
from rich.table import Table
import config

"""
Webs de interés:
- Módulo OpenAI: https://github.com/openai/openai-python
- Documentación API ChatGPT: https://platform.openai.com/docs/api-reference/chat
- Typer: https://typer.tiangolo.com
- Rich: https://rich.readthedocs.io/en/stable/
"""


def main():

    openai.api_key = config.api_key  # TU_API_KEY creada en https://platform.openai.com

    # [/bold green] propiedades del paquete rich.table
    print("💬 [bold green]ChatGPT API en Python[/bold green]")

    # Agregar la tabla visible en la consola despues de la ejecucion
    table = Table("Comando", "Descripción")
    table.add_row("exit", "Salir de la aplicación")
    table.add_row("new", "Crear una nueva conversación")

    print(table)

    # Contexto del asistente, 'Eres un asistente muy útil' hace que chatgpt de respuestas mas completas
    context = {"role": "system",
               "content": "Eres un asistente muy útil."}
    messages = [context]

    while True:

        content = __prompt()

        if content == "new":
            print("🆕 Nueva conversación creada")
            messages = [context]
            content = __prompt()

        messages.append({"role": "user", "content": content})

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages)

        response_content = response.choices[0].message.content

        messages.append({"role": "assistant", "content": response_content})

        print(f"[bold green]> [/bold green] [green]{response_content}[/green]")


# Funcion que controlara el comando de exit y agrega confirmacion [y/n] todo incluido en typer
def __prompt() -> str:  # la obligo a ser string
    prompt = typer.prompt("\n¿Sobre qué quieres hablar? ")

    if prompt == "exit":
        exit = typer.confirm("✋ ¿Estás seguro?")
        if exit:
            print("👋 ¡Hasta luego!")
            raise typer.Abort()

        return __prompt()

    return prompt


""" Esta línea de código se utiliza comúnmente en Python para indicar que el código siguiente solo debe ejecutarse si el archivo actual se está ejecutando como un programa independiente y no se está importando 
como un módulo en otro programa.

En otras palabras, cuando se ejecuta un archivo de Python, la variable especial `__name__` se establece en "__main__". Por lo tanto, si la línea `if __name__ == "__main__":` se utiliza en un archivo de Python,  
el código dentro de esta condición solo se ejecutará si se está ejecutando directamente el archivo, y no si se importa como un módulo dentro de otro programa. Esta línea de código es útil para evitar que ciertas
secciones de código se ejecuten accidentalmente cuando se importan de forma incorrecta. """
if __name__ == "__main__":
    typer.run(main)
