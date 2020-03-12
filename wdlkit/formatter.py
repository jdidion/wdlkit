import json
import re
import textwrap
from typing import Any, Callable, Dict, Optional, Sequence, cast

from jinja2 import Environment, PackageLoader, Template
from WDL import (
    Call, Conditional, Decl, Document, Env, Expr, Scatter, StructTypeDef, Task,
    Workflow, WorkflowNode, WorkflowSection
)

from wdlkit.ast import WorkflowBodyGraph


_JINJA_ENV = Environment(loader=PackageLoader("wdlkit"))
_JINJA_ENV.filters["dedent"] = textwrap.dedent
_JSON_ENCODER = json.JSONEncoder(indent=2)
_TEMPLATE_DOCUMENT = "document.wdl"
_UNQUOTE_RE = re.compile(r"^(\s+)\"(.+?)\":", re.M)
_UNQUOTE_REPL = r"\1\2:"


def _get_template(name: str) -> Template:
    return _JINJA_ENV.get_template(name)


def _frag_renderer(func: Callable, call_wrapped: bool = False):
    is_classmethod = isinstance(func, classmethod)

    if is_classmethod:
        func = cast(classmethod, func).__func__

    prefix = func.__name__[7:]

    def renderer(cls, *args, **kwargs) -> str:
        template_name = f"{prefix}.wdl.frag"

        if args:
            kwargs["value"] = args[0]

        if call_wrapped:
            kwargs = func(cls, **kwargs)

        return _get_template(template_name).render(**kwargs)

    return classmethod(renderer) if is_classmethod else renderer


def _proxy_frag_renderer(func: Callable):
    return _frag_renderer(func, True)


class Formatter:
    @classmethod
    def format_document(
        cls,
        uri: str,
        doc: Document,
        contents: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        if contents is None:
            contents = {}

        contents[uri] = _get_template(_TEMPLATE_DOCUMENT).render(
            structs=[cls.format_struct(s) for s in doc.struct_typedefs or ()],
            workflow=cls.format_workflow(doc.workflow) if doc.workflow else None,
            tasks=[cls.format_task(task) for task in (doc.tasks or ())]
        )

        if doc.imports:
            for imp in doc.imports:
                cls.format_document(imp.uri, imp.doc, contents)

        return contents

    @_proxy_frag_renderer
    @classmethod
    def format_workflow(cls, value: Workflow) -> str:
        return dict(
            name=value.name,
            inputs=cls.format_input(value.inputs or ()),
            body=cls.format_workflow_body(value.body),
            outputs=cls.format_output(value.outputs or ()),
            meta=cls.format_meta(value.meta),
            parameter_meta=cls.format_parameter_meta(value.parameter_meta),
        )

    @_proxy_frag_renderer
    @classmethod
    def format_workflow_body(cls, value: Sequence[WorkflowNode]) -> str:
        graph = WorkflowBodyGraph(*value)
        decls = []
        body = []

        for node in graph.dependency_order():
            if isinstance(node, Decl):
                decls.append(node)
                continue

            if decls:
                body.append(cls.format_declarations(decls))
                decls = []

            if isinstance(node, Call):
                body.append(cls.format_call(node))
            elif isinstance(node, WorkflowSection):
                body.append(cls.format_section(cast(WorkflowSection, node)))

        if decls:
            body.append(cls.format_declarations(decls))

        return {"value": body}

    @_proxy_frag_renderer
    @classmethod
    def format_task(cls, value: Task) -> str:
        return dict(
            name=value.name,
            inputs=cls.format_input(value.inputs or ()),
            post_inputs=cls.format_declarations(value.postinputs),
            command=cls.format_command(value.command),
            outputs=cls.format_output(value.outputs),
            runtime=cls.format_runtime(value.runtime),
            meta=cls.format_meta(value.meta),
            parameter_meta=cls.format_parameter_meta(value.parameter_meta),
        )

    @_frag_renderer
    @classmethod
    def format_struct(cls, value: Env.Binding[StructTypeDef]) -> str:
        pass

    @_frag_renderer
    @classmethod
    def format_input(cls, value: Sequence[Decl]) -> str:
        pass

    @_frag_renderer
    @classmethod
    def format_output(cls, value: Sequence[Decl]) -> str:
        pass

    @_frag_renderer
    @classmethod
    def format_declarations(cls, value: Sequence[Decl]) -> str:
        pass

    @_proxy_frag_renderer
    @classmethod
    def format_meta(cls, value: Dict[str, Any]) -> str:
        return {"value": cls._format_jsonlike(value)}

    @_proxy_frag_renderer
    @classmethod
    def format_parameter_meta(cls, value: Dict[str, Any]) -> str:
        return {"value": cls._format_jsonlike(value)}

    @classmethod
    def _format_jsonlike(cls, value: Dict[str, Any]) -> Dict[str, str]:
        # format as JSON and unquote hash keys
        return dict(
            (key, _UNQUOTE_RE.subn(_UNQUOTE_REPL, _JSON_ENCODER.encode(val))[0])
            for key, val in value.items()
        )

    @_frag_renderer
    @classmethod
    def format_call(cls, value: Call):
        pass

    @classmethod
    def format_section(cls, section: WorkflowSection) -> str:
        subgraph_content = cls.format_workflow_body(section.body)
        if isinstance(section, Conditional):
            return cls.format_conditional(section, body=subgraph_content)
        elif isinstance(section, Scatter):
            return cls.format_scatter(section, body=subgraph_content)

    @_frag_renderer
    @classmethod
    def format_conditional(cls, value: Conditional, body: str):
        pass

    @_frag_renderer
    @classmethod
    def format_scatter(cls, value: Scatter, body: str):
        pass

    @_frag_renderer
    @classmethod
    def format_command(cls, value: Expr.String):
        pass

    @_frag_renderer
    @classmethod
    def format_runtime(cls, value: Dict[str, Expr.Base]) -> str:
        pass
