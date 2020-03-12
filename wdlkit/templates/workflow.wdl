workflow {{ name }} {{ "{" }}{% if inputs %}
{{ inputs | indent(2, True) }}
{% endif %}{% if body %}
{{ body | trim() | indent(2, True) }}
{% endif %}{% if outputs %}
{{ outputs | indent(2, True) }}
{% endif %}{% if meta %}
{{ meta | indent(2, True) }}
{% endif %}{% if parameter_meta %}
{{ parameter_meta | indent(2, True) }}
{% endif %}}