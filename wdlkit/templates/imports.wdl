{% if imports %}{% for imp in imports %}
import "{{ imp.uri }}"{% if imp.namespace %} as {{ imp.namespace}}{% if imp.aliases %}{% for alias in imp.aliases %}
  alias {{ alias[0] }} as {{ alias[1] }}{% endfor %}{% endif %}{% endif %}{% endfor %}{% endif %}