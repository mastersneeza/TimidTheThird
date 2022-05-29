
using Timid.Debug;
using Timid.Lex;

namespace Timid.Parse {
    abstract class Expr {
        public interface Visitor<T> {
            T VisitBinaryExpr(Expr.BinaryExpr expr);
            T VisitLiteralExpr(Expr.LiteralExpr expr);
            T VisitUnaryExpr(Expr.UnaryExpr expr);
        }

        public abstract T Accept<T>(Visitor<T> visitor);

        Position posStart;
        Position posEnd;

        public Expr(Position posStart, Position? posEnd) {
            this.posStart = posStart.Copy();
            if (posEnd == null) {
                this.posEnd = this.posStart.Copy().Advance('\0');
            } else {
                this.posEnd = posEnd.Copy();
            }
        }

        public class BinaryExpr : Expr {
            Expr left;
            Expr right;
            Token op;
            public BinaryExpr(Expr left, Token op, Expr right) : base(left.posStart, right.posEnd) {
                this.left = left;
                this.op = op;
                this.right = right;
            }

            public override T Accept<T>(Visitor<T> visitor) {
                return visitor.VisitBinaryExpr(this);
            }
        }

        public class LiteralExpr : Expr {
            Token literal;
            public LiteralExpr(Token literal) : base(literal.posStart, literal.posEnd) {
                this.literal = literal;
            }

            public override T Accept<T>(Visitor<T> visitor) {
                return visitor.VisitLiteralExpr(this);
            }
        }

        public class UnaryExpr : Expr {
            Token op;
            Expr right;
            public UnaryExpr(Token op, Expr right) : base(op.posStart, right.posEnd) {
                this.op = op;
                this.right = right;
            }

            public override T Accept<T>(Visitor<T> visitor) {
                return visitor.VisitUnaryExpr(this);
            }
        }
    }
}