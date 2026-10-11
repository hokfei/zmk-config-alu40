#!/usr/bin/env python3
"""Generate config/private_macros.dtsi from MACRO<n> environment variables (US layout).

Usage: gen_macros.py [output.dtsi]
macro0 and macro1 are always emitted; an unset one becomes an empty stub.
"""
import os
import re
import sys

PLAIN = {c: c.upper() for c in "abcdefghijklmnopqrstuvwxyz"}
PLAIN.update({str(d): f"N{d}" for d in range(10)})
PLAIN.update({"-": "MINUS", "=": "EQUAL", "[": "LBKT", "]": "RBKT", "\\": "BSLH", ";": "SEMI",
              "'": "SQT", "`": "GRAVE", ",": "COMMA", ".": "DOT", "/": "FSLH", " ": "SPACE"})

SHIFTED = {c: f"LS({c})" for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}
SHIFTED.update({ch: f"LS(N{i})" for i, ch in zip([1, 2, 3, 4, 5, 6, 7, 8, 9, 0], "!@#$%^&*()")})
SHIFTED.update({"_": "LS(MINUS)", "+": "LS(EQUAL)", "{": "LS(LBKT)", "}": "LS(RBKT)", "|": "LS(BSLH)",
                ":": "LS(SEMI)", '"': "LS(SQT)", "~": "LS(GRAVE)", "<": "LS(COMMA)", ">": "LS(DOT)",
                "?": "LS(FSLH)"})

KEYS = {**PLAIN, **SHIFTED}


def bindings(name, text):
    out = []
    for i, ch in enumerate(text):
        if ch not in KEYS:
            sys.exit(f"{name}: unsupported character at position {i + 1}")
        out.append(f"&kp {KEYS[ch]}")
    return out


def node(name, text):
    keys = bindings(name, text) or ["&none"]
    rows = "".join("\n                " + " ".join(keys[i:i + 8]) for i in range(0, len(keys), 8))
    return (f"        {name}: {name} {{\n"
            f"            compatible = \"zmk,behavior-macro\";\n"
            f"            #binding-cells = <0>;\n"
            f"            display-name = \"{name}\";\n"
            f"            bindings = <&macro_tap{rows}\n"
            f"            >;\n"
            f"        }};\n")


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "config/private_macros.dtsi"
    texts = {}
    for key, value in os.environ.items():
        m = re.fullmatch(r"MACRO(\d+)", key)
        if m:
            texts[f"macro{int(m.group(1))}"] = value.rstrip("\r\n")
    for required in ("macro0", "macro1"):
        texts.setdefault(required, "")
    body = "".join(node(n, texts[n]) for n in sorted(texts))
    with open(out, "w", newline="\n") as f:
        f.write("/ {\n    macros {\n" + body + "    };\n};\n")
    print(f"Wrote {out} with {len(texts)} macro(s)")


if __name__ == "__main__":
    main()
