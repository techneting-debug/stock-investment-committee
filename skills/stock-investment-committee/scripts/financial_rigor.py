#!/usr/bin/env python3
"""Zero-dependency decimal calculator for stock-investment-committee.

Python 3.8+. All arithmetic uses Decimal; no network access or credentials.
"""

import argparse
import ast
import json
import operator
from decimal import Decimal, getcontext

getcontext().prec = 28


def dec(value):
    return value if isinstance(value, Decimal) else Decimal(str(value))


def money(value):
    return f"{dec(value):,.2f}"


def percent(value):
    return f"{dec(value):.2f}%"


def position(args):
    shares, cost, price = dec(args.shares), dec(args.cost), dec(args.price)
    total_cost = shares * cost
    market_value = shares * price
    pnl = market_value - total_cost
    return_pct = pnl / total_cost * 100 if total_cost else Decimal("0")
    result = {
        "shares": str(shares),
        "cost_per_share": str(cost),
        "price": str(price),
        "total_cost": str(total_cost),
        "market_value": str(market_value),
        "pnl": str(pnl),
        "return_pct": str(return_pct),
    }
    print("持仓精确计算")
    print(f"总成本: {money(total_cost)}")
    print(f"当前市值: {money(market_value)}")
    print(f"浮动盈亏: {money(pnl)}")
    print(f"收益率: {percent(return_pct)}")
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))


def market_cap(args):
    price, shares = dec(args.price), dec(args.shares)
    calculated = price * shares
    print("市值验算")
    print(f"股价: {price} {args.currency}")
    print(f"总股本: {shares}")
    print(f"计算市值: {money(calculated)} {args.currency}")
    if args.reported is not None:
        reported = dec(args.reported)
        deviation = abs(calculated - reported) / reported * 100 if reported else Decimal("0")
        status = "PASS" if deviation <= Decimal("1") else "REVIEW"
        print(f"报告市值: {money(reported)} {args.currency}")
        print(f"偏差: {percent(deviation)} [{status}]")


def cross_validate(args):
    values = {key: dec(value) for key, value in json.loads(args.values).items()}
    ordered = sorted(values.values())
    count = len(ordered)
    if count < 2:
        raise SystemExit("cross-validate requires at least two sources")
    median = ordered[count // 2] if count % 2 else (ordered[count // 2 - 1] + ordered[count // 2]) / 2
    tolerance = dec(args.tolerance)
    print(f"交叉验证: {args.field}")
    all_ok = True
    for source, value in values.items():
        deviation = abs(value - median) / abs(median) * 100 if median else Decimal("0")
        ok = deviation <= tolerance
        all_ok = all_ok and ok
        print(f"{'PASS' if ok else 'REVIEW'} {source}: {value} {args.unit}; 偏差 {percent(deviation)}")
    print(f"共识中位数: {median} {args.unit}")
    print(f"结论: {'数据一致' if all_ok else '需要核对口径'}")


def valuation(args):
    price = dec(args.price)
    print("估值验算")
    if args.eps is not None:
        eps = dec(args.eps)
        print(f"PE: {price / eps:.2f}x" if eps else "PE: N/A")
        print(f"盈利收益率: {percent(eps / price * 100)}" if price else "盈利收益率: N/A")
    if args.bvps is not None:
        bvps = dec(args.bvps)
        print(f"PB: {price / bvps:.2f}x" if bvps else "PB: N/A")
    if args.fcf_per_share is not None:
        fcf = dec(args.fcf_per_share)
        print(f"P/FCF: {price / fcf:.2f}x" if fcf else "P/FCF: N/A")
    if args.dividend is not None:
        dividend = dec(args.dividend)
        print(f"股息率: {percent(dividend / price * 100)}" if price else "股息率: N/A")


def scenario(args):
    price, eps = dec(args.price), dec(args.eps)
    growth = [dec(item) for item in args.growth]
    multiples = [dec(item) for item in args.multiple]
    labels = ["乐观", "基准", "悲观"]
    print("三情景估值")
    print("情景 | 年增速 | 目标EPS | 目标倍数 | 目标价 | 相对当前")
    for label, rate, multiple in zip(labels, growth, multiples):
        future_eps = eps * ((Decimal("1") + rate) ** args.years)
        target = future_eps * multiple
        upside = (target / price - 1) * 100 if price else Decimal("0")
        print(f"{label} | {percent(rate * 100)} | {future_eps:.4f} | {multiple}x | {target:.2f} | {percent(upside)}")


OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def evaluate(node):
    if isinstance(node, ast.Expression):
        return evaluate(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return dec(node.value)
    if isinstance(node, ast.BinOp) and type(node.op) in OPS:
        return OPS[type(node.op)](evaluate(node.left), evaluate(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
        return OPS[type(node.op)](evaluate(node.operand))
    raise ValueError("Only numeric arithmetic is allowed")


def calculate(args):
    result = evaluate(ast.parse(args.expression, mode="eval"))
    print(f"精确值: {result}")


def build_parser():
    parser = argparse.ArgumentParser(description="股票投委会精确财务计算器")
    commands = parser.add_subparsers(dest="command", required=True)

    p = commands.add_parser("position", help="计算持仓成本、市值和盈亏")
    p.add_argument("--shares", required=True)
    p.add_argument("--cost", required=True)
    p.add_argument("--price", required=True)
    p.add_argument("--json", action="store_true")
    p.set_defaults(run=position)

    p = commands.add_parser("market-cap", help="验算股价乘总股本")
    p.add_argument("--price", required=True)
    p.add_argument("--shares", required=True)
    p.add_argument("--reported")
    p.add_argument("--currency", default="")
    p.set_defaults(run=market_cap)

    p = commands.add_parser("cross-validate", help="核对多个来源的同一数据")
    p.add_argument("--field", required=True)
    p.add_argument("--values", required=True, help='JSON, e.g. {"annual report": 10, "exchange": 10.1}')
    p.add_argument("--unit", default="")
    p.add_argument("--tolerance", default="1")
    p.set_defaults(run=cross_validate)

    p = commands.add_parser("valuation", help="计算PE、PB、P/FCF和股息率")
    p.add_argument("--price", required=True)
    p.add_argument("--eps")
    p.add_argument("--bvps")
    p.add_argument("--fcf-per-share")
    p.add_argument("--dividend")
    p.set_defaults(run=valuation)

    p = commands.add_parser("scenario", help="计算三年复合增长和目标估值")
    p.add_argument("--price", required=True)
    p.add_argument("--eps", required=True)
    p.add_argument("--growth", nargs=3, required=True, metavar=("BULL", "BASE", "BEAR"))
    p.add_argument("--multiple", nargs=3, required=True, metavar=("BULL", "BASE", "BEAR"))
    p.add_argument("--years", type=int, default=3)
    p.set_defaults(run=scenario)

    p = commands.add_parser("calc", help="安全计算纯数字算式")
    p.add_argument("expression")
    p.set_defaults(run=calculate)
    return parser


if __name__ == "__main__":
    options = build_parser().parse_args()
    options.run(options)

