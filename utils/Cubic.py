class Cubic:
    def __init__(self, x, y):
        """
        Initializes the interpolation class; x is the independent variable, and y is the corresponding dependent variable.
        It assumes that x is sorted in ascending order and has length n.
        """
        self.x = x
        self.y = y
        self.n = len(x) - 1  # Number of intervals in x and y
        self.h = [x[i + 1] - x[i] for i in range(self.n)]  # Distance between adjacent points
        self.a = y[:]  # Coefficient a is the y values themselves

        # Calculate coefficients b, c, and d
        self.b, self.c, self.d = self.__compute_coefficients()

    def __compute_coefficients(self):
        """Calculates the coefficients b, c, and d for cubic spline interpolation."""
        # Construct the tridiagonal matrix and the right-side vector
        A = [[0] * (self.n + 1) for _ in range(self.n + 1)]
        b = [0] * (self.n + 1)

        # Set boundary conditions (natural boundary, second derivative is 0)
        A[0][0] = 1
        A[self.n][self.n] = 1

        # Set the middle part of the matrix
        for i in range(1, self.n):
            A[i][i - 1] = self.h[i - 1]
            A[i][i] = 2 * (self.h[i - 1] + self.h[i])
            A[i][i + 1] = self.h[i]
            b[i] = 3 * ((self.a[i + 1] - self.a[i]) / self.h[i] - (self.a[i] - self.a[i - 1]) / self.h[i - 1])

        # Solve the tridiagonal system A * c = b
        c = self.__solve_tridiagonal(A, b)

        # Calculate b and d
        b = [0] * self.n
        d = [0] * self.n
        for i in range(self.n):
            b[i] = (self.a[i + 1] - self.a[i]) / self.h[i] - self.h[i] * (2 * c[i] + c[i + 1]) / 3
            d[i] = (c[i + 1] - c[i]) / (3 * self.h[i])

        return b, c[:-1], d

    def __solve_tridiagonal(self, A, b):
        """Solves the linear system of equations for a tridiagonal matrix."""
        n = len(b)
        c_prime = [0] * n
        d_prime = [0] * n
        x = [0] * n

        # Forward elimination
        c_prime[0] = A[0][1] / A[0][0]
        d_prime[0] = b[0] / A[0][0]
        for i in range(1, n - 1):
            denom = A[i][i] - A[i][i - 1] * c_prime[i - 1]
            c_prime[i] = A[i][i + 1] / denom
            d_prime[i] = (b[i] - A[i][i - 1] * d_prime[i - 1]) / denom

        d_prime[n - 1] = (b[n - 1] - A[n - 1][n - 2] * d_prime[n - 2]) / (
                A[n - 1][n - 1] - A[n - 1][n - 2] * c_prime[n - 2])

        # Back substitution
        x[n - 1] = d_prime[n - 1]
        for i in range(n - 2, -1, -1):
            x[i] = d_prime[i] - c_prime[i] * x[i + 1]

        return x

    def evaluate(self, x_eval):
        """Evaluates the interpolation function for input x_eval and returns the corresponding interpolated values."""
        results = []

        for x_val in x_eval:
            # Determine which interval the value is in
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
        """Finds the interpolation interval for the given x_val."""
        if x_val < self.x[0] or x_val > self.x[-1]:
            return None  # Return None if x value is out of bounds
        for i in range(self.n):
            if self.x[i] <= x_val <= self.x[i + 1]:
                return i
        return None


class Pchip:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.h = [x[i + 1] - x[i] for i in range(len(x) - 1)]  # Length of each interval
        self.slopes = [(y[i + 1] - y[i]) / self.h[i] for i in range(len(y) - 1)]
        self.derivatives = self.compute_derivatives()
        self.coefficients = self.compute_coefficients()

    def compute_derivatives(self):
        """Calculates the derivative at each point to maintain monotonicity."""
        n = len(self.slopes) + 1
        derivatives = [0] * n

        # Compute derivatives, ensuring monotonicity
        for i in range(1, n - 1):
            if self.slopes[i - 1] * self.slopes[i] <= 0:
                derivatives[i] = 0
            else:
                w1 = 2 * self.h[i] + self.h[i - 1]
                w2 = self.h[i] + 2 * self.h[i - 1]
                derivatives[i] = (w1 + w2) / (w1 / self.slopes[i - 1] + w2 / self.slopes[i])

        # Boundary derivatives
        derivatives[0] = self.slopes[0]
        derivatives[-1] = self.slopes[-1]

        return derivatives

    def compute_coefficients(self):
        """Calculates the polynomial coefficients for each interval."""
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
        """Interpolates at the given x_new."""
        for i in range(len(self.x) - 1):
            if self.x[i] <= x_new <= self.x[i + 1]:
                c0, c1, c2, c3 = self.coefficients[i]
                dx = x_new - self.x[i]
                return c0 + c1 * dx + c2 * dx ** 2 + c3 * dx ** 3
        raise ValueError("x_new out of bounds.")
