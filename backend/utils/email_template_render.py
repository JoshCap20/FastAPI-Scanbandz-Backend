from jinja2 import Environment, FileSystemLoader


def render_email_template(variables: dict, template_name: str) -> str:
    env = Environment(loader=FileSystemLoader("backend/assets/communication"))
    template = env.get_template(template_name)
    return template.render(**variables)
