class Cubic:
    def __init__(self, x, y):
        """
        初始化插值类，x为自变量，y为对应的因变量
        这里假设 x 是升序排列的，并且长度为 n
        """
        self.x = x
        self.y = y
        self.n = len(x) - 1  # x 和 y 的区间数
        self.h = [x[i + 1] - x[i] for i in range(self.n)]  # 相邻点之间的距离
        self.a = y[:]  # 系数 a 就是 y 值本身

        # 计算系数 b, c, d
        self.b, self.c, self.d = self.__compute_coefficients()

    def __compute_coefficients(self):
        """计算三次样条插值的系数 b, c, d"""
        # 构建三对角矩阵和右边的向量
        A = [[0] * (self.n + 1) for _ in range(self.n + 1)]
        b = [0] * (self.n + 1)

        # 设置边界条件（自然边界，二阶导数为0）
        A[0][0] = 1
        A[self.n][self.n] = 1

        # 设置矩阵的中间部分
        for i in range(1, self.n):
            A[i][i - 1] = self.h[i - 1]
            A[i][i] = 2 * (self.h[i - 1] + self.h[i])
            A[i][i + 1] = self.h[i]
            b[i] = 3 * ((self.a[i + 1] - self.a[i]) / self.h[i] - (self.a[i] - self.a[i - 1]) / self.h[i - 1])

        # 求解三对角线性方程组 A * c = b
        c = self.__solve_tridiagonal(A, b)

        # 计算 b 和 d
        b = [0] * self.n
        d = [0] * self.n
        for i in range(self.n):
            b[i] = (self.a[i + 1] - self.a[i]) / self.h[i] - self.h[i] * (2 * c[i] + c[i + 1]) / 3
            d[i] = (c[i + 1] - c[i]) / (3 * self.h[i])

        return b, c[:-1], d

    def __solve_tridiagonal(self, A, b):
        """求解三对角矩阵的线性方程组"""
        n = len(b)
        c_prime = [0] * n
        d_prime = [0] * n
        x = [0] * n

        # 前向消去
        c_prime[0] = A[0][1] / A[0][0]
        d_prime[0] = b[0] / A[0][0]
        for i in range(1, n - 1):
            denom = A[i][i] - A[i][i - 1] * c_prime[i - 1]
            c_prime[i] = A[i][i + 1] / denom
            d_prime[i] = (b[i] - A[i][i - 1] * d_prime[i - 1]) / denom

        d_prime[n - 1] = (b[n - 1] - A[n - 1][n - 2] * d_prime[n - 2]) / (
                A[n - 1][n - 1] - A[n - 1][n - 2] * c_prime[n - 2])

        # 回代求解
        x[n - 1] = d_prime[n - 1]
        for i in range(n - 2, -1, -1):
            x[i] = d_prime[i] - c_prime[i] * x[i + 1]

        return x

    def evaluate(self, x_eval):
        """插值求值函数，输入x_eval并返回对应的插值值"""
        results = []

        for x_val in x_eval:
            # 确定在哪个区间
            idx = self.__find_interval(x_val)
            if idx is None:
                results.append(None)
                continue

            dx = x_val - self.x[idx]
            result = (
                    self.a[idx] +
                    self.b[idx] * dx +
                    self.c[idx] * dx ** 2 +
                    self.d[idx] * dx ** 3
            )
            results.append(result)

        return results

    def __find_interval(self, x_val):
        """找到 x_val 所在的插值区间"""
        if x_val < self.x[0] or x_val > self.x[-1]:
            return None  # 如果x值超出范围，返回None
        for i in range(self.n):
            if self.x[i] <= x_val <= self.x[i + 1]:
                return i
        return None


class Pchip:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.h = [x[i + 1] - x[i] for i in range(len(x) - 1)]  # 每个间隔的长度
        self.slopes = [(y[i + 1] - y[i]) / self.h[i] for i in range(len(y) - 1)]
        self.derivatives = self.compute_derivatives()
        self.coefficients = self.compute_coefficients()

    def compute_derivatives(self):
        """计算每个点的导数以保持单调性。"""
        n = len(self.slopes) + 1
        derivatives = [0] * n

        # 计算导数, 确保单调性
        for i in range(1, n - 1):
            if self.slopes[i - 1] * self.slopes[i] <= 0:
                derivatives[i] = 0
            else:
                w1 = 2 * self.h[i] + self.h[i - 1]
                w2 = self.h[i] + 2 * self.h[i - 1]
                derivatives[i] = (w1 + w2) / (w1 / self.slopes[i - 1] + w2 / self.slopes[i])

        # 边界导数
        derivatives[0] = self.slopes[0]
        derivatives[-1] = self.slopes[-1]

        return derivatives

    def compute_coefficients(self):
        """计算每个区间的多项式系数。"""
        coefficients = []
        for i in range(len(self.slopes)):
            dy0 = self.derivatives[i]
            dy1 = self.derivatives[i + 1]
            c0 = self.y[i]
            c1 = dy0
            c2 = (3 * self.slopes[i] - 2 * dy0 - dy1) / self.h[i]
            c3 = (dy0 + dy1 - 2 * self.slopes[i]) / (self.h[i] ** 2)
            coefficients.append((c0, c1, c2, c3))
        return coefficients

    def __call__(self, x_new):
        """在 x_new 上进行插值。"""
        for i in range(len(self.x) - 1):
            if self.x[i] <= x_new <= self.x[i + 1]:
                c0, c1, c2, c3 = self.coefficients[i]
                dx = x_new - self.x[i]
                return c0 + c1 * dx + c2 * dx ** 2 + c3 * dx ** 3
        raise ValueError("x_new out of bounds.")
