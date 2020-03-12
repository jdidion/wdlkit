if ({{ value.expr }}) {
  {{ body | trim() | indent(2, False) }}
}