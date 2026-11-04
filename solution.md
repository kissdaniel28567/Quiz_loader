Here is a complete, precise study guide answering every question and topic from the document.

---

# Part 1: Machine Learning & Deep Learning Foundations (Lectures 1–6)

---

### Core Concepts & Definitions

* **What are the inputs to the hypothesis function ($h_\theta$)?**
  * The input feature vector $\mathbf{x}$ (or feature matrix $X$ for a batch of examples) and the model parameters/weights $\theta$ (or $W, b$).
* **What are the outputs (the value) of the hypothesis function?**
  * The prediction $\hat{y}$ (or vector of predictions $\mathbf{\hat{y}}$):
    * In **regression**: a continuous numerical value (or vector of continuous values).
    * In **binary classification**: an estimated probability $P(y=1|\mathbf{x}) \in [0, 1]$ (or a discrete class label after thresholding).
    * In **multi-class classification**: a probability distribution over classes (vector summing to 1).
* **What can be the format of a label?**
  * **Scalar**: standard single-target regression ($y \in \mathbb{R}$) or binary classification ($y \in \{0, 1\}$).
  * **Vector**: multi-output regression, multi-label classification, or one-hot encoded multi-class labels ($\mathbf{y} \in \{0, 1\}^K$).
  * **Matrix / Tensor**: structured prediction, such as image segmentation masks (matrix) or video annotations.
* **What are the constituents of a data point in supervised learning?**
  * An **input feature vector** $\mathbf{x} = [x_1, x_2, \dots, x_n]^T$ and its corresponding **ground truth label/target** $y$.
* **What is the role of the loss function?**
  * To quantify the discrepancy (error/penalty) between the model’s prediction $\hat{y} = h_\theta(\mathbf{x})$ and the true target $y$ for a single instance (or averaged over a dataset as a cost function $J(\theta)$). It guides optimization/learning.
* **Can the value of the loss function be a scalar / vector / matrix?**
  * The final evaluated loss / cost $J(\theta)$ is always a **scalar** (a single real number) so that it can be minimized. (Individual sample losses in a batch may form a vector before reduction/averaging, but the objective function itself is scalar).
* **In reinforcement learning, what form of feedback do we get from the environment? How is it different from supervised learning?**
  * **RL feedback**: A numerical **reward signal** (often delayed, sparse, and evaluative rather than instructive). It tells the agent *how good or bad* an action was, not the *correct action*.
  * **Supervised learning feedback**: Explicit **ground truth labels** for every single training instance (instructive feedback specifying the exact correct answer).

---

### Task Categorization

| Task | Domain | Goal |
| :--- | :--- | :--- |
| **Regression** | Supervised | Predict a continuous numerical value given input features. |
| **Classification** | Supervised | Predict a discrete categorical class label given input features. |
| **Clustering** | Unsupervised | Group unlabeled data into clusters based on inherent similarity. |
| **Dimensionality Reduction** | Unsupervised | Compress data to fewer dimensions while preserving key structure/variance (e.g., PCA). |
| **Denoising** | Supervised or Self-supervised / Unsupervised | Reconstruct clean, uncorrupted signals from noisy inputs. |

* **Is linear regression used for regression or classification? Supervised or unsupervised?**
  * **Regression**; **Supervised learning**.
* **Is logistic regression used for regression or classification? Supervised or unsupervised?**
  * **Classification** (despite the name "regression"); **Supervised learning**.

---

### Scenario A: Predicting Cholesterol Level (Continuous Target)
*Attributes: weight, age, height, sex ($n = 4$ features). Training set: $m = 200$ patients.*

* **Linear vs. Logistic regression?**
  * **Linear regression** (cholesterol level is a continuous numerical variable).
* **Number of parameters ($\theta$)?**
  * **5 parameters**: 4 weights for the features + 1 bias/intercept term ($\theta_0, \theta_1, \theta_2, \theta_3, \theta_4$).
* **What loss function should we use?**
  * **Mean Squared Error (MSE)** (Least Squares loss).
* **Matrix hypothesis $h_\theta(X) = X\theta$ (where $X$ includes the intercept column of 1s):**
  * **Shape of $X$**: $(m, n + 1) = \mathbf{(200, 5)}$
  * **Shape of $\theta$**: $(n + 1, 1) = \mathbf{(5, 1)}$ (or 1D array of length $5$)
  * **Shape of $h_\theta(X)$**: $(m, 1) = \mathbf{(200, 1)}$
  * **Range of values in $h_\theta(X)$**: $(-\infty, +\infty)$ (all real numbers $\mathbb{R}$).
  * **Are the age values inside $\theta$ or $X$?**
    * Inside **$X$** (patient data are features).
  * **Do we minimize $X$ during learning?** **NO** ($X$ is fixed training data).
  * **Do we minimize $h_\theta(X)$ during learning?** **NO** (that would predict arbitrarily low values).
  * **Do we minimize $\theta$ during learning?** **NO** (minimizing $\theta$ directly is not the goal; regularization only penalizes large weights, but learning minimizes the *loss*).
  * **What do we minimize during learning?** The **cost/loss function $J(\theta)$** (e.g., MSE).
* **Scalar hypothesis for a single instance: $h_\theta(\mathbf{x}) = \theta^T \mathbf{x} = \sum_{i=0}^n \theta_i x_i$:**
  * **Is $h_\theta(\mathbf{x})$ a vector or scalar?** **Scalar** (a single predicted cholesterol value).
  * **Range of $h_\theta(\mathbf{x})$?** $(-\infty, +\infty)$.
  * **Is patient age assigned to $\theta$ or $x$?** Assigned to an **$x_i$** feature value.
* **Geometric interpretation:**
  * **1 input variable** plotted on $(x, y)$ axes: A **straight line** ($y = \theta_1 x_1 + \theta_0$).
  * **2 input variables** plotted on $(x_1, x_2, y)$ axes: A **flat 2D plane** in 3D space.
* **Normal Equation $\theta = (X^T X + \lambda I)^{-1} X^T \mathbf{y}$:**
  * **Shape of $X$**: $(200, 5)$
  * **Shape of $\mathbf{y}$**: $(200, 1)$
  * **Shape of $\theta$**: $(5, 1)$
  * **Where are cholesterol levels placed?** In **$\mathbf{y}$** (the target vector).
  * **What is the $I$ matrix?** The **identity matrix** (size $(n+1) \times (n+1) = 5 \times 5$, typically with a $0$ at top-left $I_{0,0}=0$ so the bias is not regularized).
* **Guaranteed to find globally optimal parameters with gradient descent (small enough step size)?**
  * **Linear Regression with MSE**: **YES**. MSE with a linear model is strictly convex (a single global minimum, no local minima).
  * **Multi-Layer Perceptron (MLP) with MSE**: **NO**. Neural networks are non-convex; gradient descent can get stuck in local minima or saddle points.

---

### Feature Scaling

* **Purpose:** Ensures features have comparable numerical ranges so that the loss contours are spherical rather than elongated ellipses. This accelerates gradient descent convergence and prevents features with large magnitudes from dominating.
* **If we do NOT use feature scaling:**
  * Gradient descent oscillates, takes a very inefficient zigzag path, converges significantly slower, or diverges if the learning rate is too large.
* **Min-Max Scaling vs. Standardization robustness to outliers:**
  * **Standardization** ($z = \frac{x - \mu}{\sigma}$) is **more robust** to outliers.
  * *Reason:* Min-Max scaling ($x' = \frac{x - x_{min}}{x_{max} - x_{min}}$) directly uses the extreme values $x_{min}$ and $x_{max}$, which compresses normal data into a tiny interval if an extreme outlier exists.

---

### Scenario B: Distinguishing Sick vs. Healthy Patients (Binary Classification)
*Attributes: 2 blood test values ($n = 2$). Training set: $m = 100$ patients.*

* **Linear vs. Logistic regression?**
  * **Logistic regression**.
* **Number of parameters ($\theta$)?**
  * **3 parameters** ($\theta_0$ bias, $\theta_1, \theta_2$ feature weights).
* **Loss function:**
  * **Binary Cross-Entropy Loss** (also called Log Loss / Negative Log-Likelihood).
* **Matrix hypothesis $h_\theta(X) = g(X\theta)$ where $g(z) = \frac{1}{1 + e^{-z}}$:**
  * **Shape of $X$**: $\mathbf{(100, 3)}$ (with bias column).
  * **Shape of $\theta$**: $\mathbf{(3, 1)}$.
  * **Shape of $h_\theta(X)$**: $\mathbf{(100, 1)}$.
  * **Range of values in $h_\theta(X)$**: **$(0, 1)$** (probabilities).
  * **Are blood test results in $\theta$ or $X$?** In **$X$**.
  * **What do we minimize during learning?** The **Binary Cross-Entropy cost function $J(\theta)$**. (Do *not* minimize $X, \theta, h_\theta(X),$ or $g$).
* **Scalar hypothesis $h_\theta(\mathbf{x}) = g(\theta^T \mathbf{x})$:**
  * **Is $h_\theta(\mathbf{x})$ a vector or scalar?** **Scalar**.
  * **Range of $\theta^T \mathbf{x}$ (the logit $z$)?** $(-\infty, +\infty)$.
  * **Range of $h_\theta(\mathbf{x})$?** $(0, 1)$.
  * **Blood test results assigned to:** **$x_i$**.

---

### Loss Functions Formulas & Analysis

Standard Cost Functions:
1. **Mean Squared Error (MSE)**:
   $$J(\theta) = \frac{1}{2m} \sum_{i=1}^m \left(h_\theta(\mathbf{x}^{(i)}) - y^{(i)}\right)^2$$
   * Task: **Regression**.
   * $m$: Total number of training examples.
   * $i$: Indexes training examples.
   * $J(\theta)$: **Scalar**.
2. **Binary Cross-Entropy**:
   $$J(\theta) = -\frac{1}{m} \sum_{i=1}^m \left[ y^{(i)} \log(h_\theta(\mathbf{x}^{(i)})) + (1 - y^{(i)}) \log(1 - h_\theta(\mathbf{x}^{(i)})) \right]$$
   * Task: **Binary Classification**.
3. **Categorical Cross-Entropy (Multi-Class)**:
   $$J(\theta) = -\frac{1}{m} \sum_{i=1}^m \sum_{k=1}^K y_k^{(i)} \log(\hat{y}_k^{(i)})$$
   * Task: **Multi-class classification** (where $k$ indexes classes).
4. **Regularization term**:
   $$\frac{\lambda}{2m} \sum_{j=1}^n \theta_j^2$$
   * $j$: Indexes the **feature weights/parameters** (excluding bias $j=0$).

---

### Multi-Layer Perceptron (MLP)

Given 2-layer MLP hypothesis: $h(x) = g_2(W_2 \cdot g_1(W_1 x + b_1) + b_2)$

* **Task: Regression with 20 input variables, 1 continuous output, 10 hidden neurons:**
  * **Parameters in 1st layer ($W_1, b_1$):**
    * $W_1 \in \mathbb{R}^{10 \times 20} \implies 200$ weights.
    * $b_1 \in \mathbb{R}^{10} \implies 10$ biases.
    * Layer 1 total = **210 parameters**.
  * **Parameters in 2nd layer ($W_2, b_2$):**
    * $W_2 \in \mathbb{R}^{1 \times 10} \implies 10$ weights.
    * $b_2 \in \mathbb{R}^{1} \implies 1$ bias.
    * Layer 2 total = **11 parameters**.
  * **Total parameters in the network:** $210 + 11 = \mathbf{221 \text{ parameters}}$.
* **Activations for Regression:**
  * **Should we omit $g_1$?** **NO!** Omitting $g_1$ collapses the network into a simple linear model.
  * **Should we omit $g_2$?** **YES** (or use the identity function $g_2(z) = z$) so the output can predict any unbounded real value.
  * **Should $g_2$ be a sigmoid?** **NO!** Sigmoid restricts the output to $(0, 1)$, which cannot predict arbitrary continuous targets.
* **For Binary Classification:**
  * Output layer has 1 neuron; $g_2$ should be **Sigmoid**; Loss is **Binary Cross-Entropy**.
* **For Multi-Class Classification ($K$ classes):**
  * Output layer has $K$ neurons; $g_2$ should be **Softmax**; Loss is **Categorical Cross-Entropy**.
* **Common Activation Functions and Ranges:**
  * **Sigmoid**: $\sigma(z) = \frac{1}{1 + e^{-z}} \in (0, 1)$ (S-shaped curve).
  * **Tanh**: $\tanh(z) = \frac{e^z - e^{-z}}{e^z + e^{-z}} \in (-1, 1)$ (Zero-centered S-curve).
  * **ReLU**: $\max(0, z) \in [0, +\infty)$ ($0$ for $z \le 0$, line with slope 1 for $z > 0$).
  * **Leaky ReLU**: $\max(\alpha z, z) \in (-\infty, +\infty)$ with a small slope $\alpha$ for $z < 0$.

---

### Overfitting, Regularization, and Training Dynamics

* **Effect of dataset size on overfitting:**
  * **Decrease training examples:** Overfitting **increases** (becomes more severe).
  * **Increase training examples:** Overfitting **decreases**.
  * **Decrease test examples:** Overfitting severity **does NOT change** (generalization ability is an intrinsic property of the trained model; test size only affects evaluation metric variance).
* **Effect of model capacity on overfitting:**
  * **Increase model parameters:** Overfitting **increases** (model has higher capacity to memorize noise).
  * **Decrease model parameters:** Overfitting **decreases**.
* **Early Stopping:**
  * **Purpose:** Prevent overfitting by stopping training before the model starts fitting noise in the training set.
  * **When to stop?** When the **validation loss** stops improving and begins consistently increasing.
  * **Should we stop when the training loss begins to increase?** **NO** (training loss typically continues decreasing; it is validation loss divergence that matters).
  * **Validation loss increases while training loss decreases:** A classic textbook indicator that **overfitting is occurring**.
* **Parameters vs. Hyperparameters:**
  * **Parameters ($W, b$):** Learned automatically using gradient-based optimization (**SGD, Adam**).
  * **Hyperparameters (learning rate, layer count, batch size):** Set before training and tuned via grid search, random search, or Bayesian optimization (NOT directly trained with gradient descent).
* **Mini-Batch SGD vs. Pure SGD:**
  * **Pure SGD (batch size = 1):** Computes gradient on a single training example per step.
  * **Increasing batch size:**
    * Gradient estimates become less noisy (smoother trajectory).
    * Better hardware utilization (GPU parallelism).
    * Requires fewer steps per epoch, but each step is computationally more expensive.
  * **Decreasing batch size:**
    * More stochasticity/noise in gradient steps (can help escape sharp local minima).
    * Lower memory footprint.
    * Slower runtime per epoch due to underutilized matrix parallelism.

---

### Computational Graph & Backpropagation

By the **Chain Rule**: $\frac{\partial J}{\partial x} = \frac{\partial J}{\partial \text{output}} \cdot \frac{\partial \text{output}}{\partial x}$

1. **Square node:** $c = b^2$
   * Given $\text{grad\_c} = \frac{\partial J}{\partial c}$.
   * $\frac{\partial c}{\partial b} = 2b$.
   * $$\mathbf{\text{grad\_b} = \text{grad\_c} \cdot 2b}$$
   *(Note: $\text{grad\_c} \cdot 2c$ is incorrect!)*

2. **Addition node:** $c = a + b$
   * Given $\text{grad\_c} = \frac{\partial J}{\partial c}$.
   * $\frac{\partial c}{\partial a} = 1$ and $\frac{\partial c}{\partial b} = 1$.
   * $$\mathbf{\text{grad\_a} = \text{grad\_c}}, \quad \mathbf{\text{grad\_b} = \text{grad\_c}}$$

---

# Part 2: NumPy Essentials

---

### Array Attributes (`my_array = np.ndarray`)

* **Can `my_array.shape` be `(5, 6)`?** **YES** (2D array).
* **Can `my_array.shape` be `(1,)`?** **YES** (1D array of 1 element).
* **Can `my_array.shape` be `(0, 1, 0)`?** **YES** (valid 3D array with 0 elements).
* **Can `my_array.shape` be `12`?** **NO** (shape is always a `tuple`, e.g., `(12,)`).
* **Can `my_array.dtype` be `(5, 6)`?** **NO** (dtype is a data type object, like `float64`, `int32`).
* **Can `my_array.size` be `(5, 6)`?** **NO** (`size` is always a scalar integer representing total element count).
* **Can `my_array.size` be `12`?** **YES** (e.g. for shape `(3, 4)`).
* **Can `my_array.ndim` be `(5, 6)`?** **NO** (`ndim` is always a scalar integer representing the number of axes).

---

### Slicing & Indexing (Array shape `(32, 5)`)

* `my_array[:, :]` $\implies \mathbf{(32, 5)}$
* `my_array[:, 1]` $\implies \mathbf{(32,)}$ (single integer index drops that axis)
* `my_array[1, :]` $\implies \mathbf{(5,)}$ (single integer index drops that axis)
* `my_array[1:, :]` $\implies \mathbf{(31, 5)}$
* `my_array[0, :-1]` $\implies \mathbf{(4,)}$
* `my_array[[0], :]` $\implies \mathbf{(1, 5)}$ (list indexing preserves the axis)
* `my_array[[-1, -1], -1]` $\implies \mathbf{(2,)}$ (selects last column for rows -1 and -1)

---

### Broadcasting Rules
`my_array1` shape: `(32, 5)`

* `my_array1 + my_array2` where `my_array2` shape is `(32,)`:
  * **Raises ValueError: YES**.
  * *Reason:* Trailing dimension 5 cannot broadcast with 32.
* `my_array1 + my_array2[:, None]` where `my_array2[:, None]` shape is `(32, 1)`:
  * **Raises ValueError: NO**.
  * *Resulting shape:* `(32, 5)`.
* `my_array1 + my_array2[None, :]` where `my_array2[None, :]` shape is `(1, 32)`:
  * **Raises ValueError: YES**.
  * *Reason:* Dimension 32 does not match 5.
* `my_array1 + 1`:
  * **Raises ValueError: NO** (scalar broadcasts to all shapes).

---

### Array Operations & Reductions (Array shape `(32, 5)`)

* `my_array < 0` $\implies \mathbf{(32, 5)}$ (boolean array)
* `my_array.T` $\implies \mathbf{(5, 32)}$
* `my_array.T.T` $\implies \mathbf{(32, 5)}$
* `my_array + my_array` $\implies \mathbf{(32, 5)}$
* `my_array + my_array[:, None, :]`:
  * Shapes: `(32, 5)` aligned with `(32, 1, 5)` $\implies$ broadcasts to $\mathbf{(32, 32, 5)}$.
* `np.mean(my_array, axis=0)` $\implies \mathbf{(5,)}$ (collapses axis 0)
* `np.mean(my_array, axis=1)` $\implies \mathbf{(32,)}$ (collapses axis 1)
* **Will `type(np.sum(my_array, axis=0))` be `numpy.ndarray`?** **YES**.
* **Will `type(np.sum(my_array))` be `numpy.ndarray`?** **NO** (it returns a numpy scalar, such as `np.int64` or `np.float64`).

---

### Array Transformations (`my_array = np.arange(4).reshape(2, -1)`)
*Here `my_array` has shape `(2, 2)` and elements `[[0, 1], [2, 3]]`.*

* Shape of `my_array` $\implies \mathbf{(2, 2)}$
* Shape of `my_array * 2 + 1` $\implies \mathbf{(2, 2)}$
* Shape of `my_array[my_array > 0]` $\implies \mathbf{(3,)}$ (boolean masking flattens to 1D)
* Shape of `my_array[(my_array > 0) & (my_array % 2 == 0)]` $\implies \mathbf{(1,)}$ (only value `2` satisfies this)
* Shape of `my_array * my_array.reshape(2, 2, -1)`:
  * `(2, 2)` broadcasts with `(2, 2, 1)` $\implies \mathbf{(2, 2, 2)}$.

---

### Memory Management: Views vs. Copies

When modifying `my_array2[:] = 99`, will original `my_array` be affected?

* `my_array2 = my_array.reshape(2, 2)`:
  * **Affected: YES** (reshape returns a **view**).
* `my_array2 = my_array.T`:
  * **Affected: YES** (transpose returns a **view**).
* `my_array2 = np.append(my_array, 42)`:
  * **Affected: NO** (`np.append` allocates a new array / **copy**).
* `my_array2 = my_array[1:2]`:
  * **Affected: YES** (basic slicing returns a **view**).
* `my_array2 = my_array[[1, 2]]`:
  * **Affected: NO** (fancy/integer list indexing returns a **copy**).
* `my_array2 = my_array[my_array < 2]`:
  * **Affected: NO** (boolean indexing returns a **copy**).
* `my_array2 = my_array + my_array`:
  * **Affected: NO** (arithmetic operations return a **new array**).

---

### Array Functions & Operations

Given `my_array = np.arange(4).reshape(2, -1)`:
*Matrix:*
$$\begin{bmatrix} 0 & 1 \\ 2 & 3 \end{bmatrix}$$

* `np.count_nonzero(my_array == 0)` $\implies \mathbf{1}$
* `np.any(my_array == 0)` $\implies \mathbf{True}$
* `np.all(my_array == 0, axis=1)` $\implies \mathbf{array([False, False])}$

Given `my_array = np.array([3, 1, 2])`:

* `np.unique(my_array)` $\implies \mathbf{array([1, 2, 3])}$ (returns sorted unique elements)
* `np.unique(my_array == 0)` $\implies \mathbf{array([False])}$ (all elements are non-zero)
* `np.bincount(my_array)` $\implies \mathbf{array([0, 1, 1, 1])}$
  *(counts occurrences of indices 0, 1, 2, 3)*
* `np.sort(my_array)[::-1]` $\implies \mathbf{array([3, 2, 1])}$
* `np.argsort(my_array)` $\implies \mathbf{array([1, 2, 0])}$
  *(indices of elements in ascending order: value 1 is at index 1, value 2 at index 2, value 3 at index 0)*
* `my_array[my_array != 0]` $\implies \mathbf{array([3, 1, 2])}$