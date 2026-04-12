# 全同态加密十（几）年的发展历程

> **演讲者**: Craig Gentry (Algorand Foundation)
> **会议**: EUROCRYPT 2021 邀请报告
> **翻译/字幕**: 刘巍然（学酥）
> **原始视频**: [Bilibili BV1rY411V7Ko](https://www.bilibili.com/video/BV1rY411V7Ko/)

---

## 第一部分：FHE的起源与发展概述 (00:00 - 10:00)

![Slide 1](images/slide_0001.jpg)

Craig Gentry, a research fellow at the Algorand Foundation and renowned cryptographer, delivered a talk titled *Decade or so of FHE encryption*. He began by acknowledging the foundational work of Rivest, Adleman, and Dertouzos in 1978, who observed the multiplicative property of RSA ciphertexts, laying the groundwork for what would later become encrypted cloud computing. This concept allows data to remain encrypted while being processed, enabling secure queries without exposing the underlying data. *The only thing that should leak about the data is the length of the data*, Gentry noted, emphasizing the importance of maintaining data privacy.

![Slide 5](images/slide_0005.jpg)

Gentry's 2009 breakthrough was the first plausibly secure fully homomorphic encryption (FHE) scheme, which introduced the idea of *bootstrapping*—a self-referential technique where the scheme decrypts itself using an encrypted secret key. Despite its initial impracticality, this work sparked rapid advancements. Over the next decade, FHE evolved through four generations, with significant improvements in efficiency and usability. The second generation, for instance, leveraged the learning with errors (LWE) problem and introduced techniques like modulus reduction and SIMD operations, drastically reducing computational overhead.

![Slide 10](images/slide_0010.jpg)

The talk also explored the current state of FHE, where Gentry aimed to *divorce it from lattices a little bit* and present it from a mathematician's perspective, focusing on hardening homomorphisms for semantic security. He highlighted the growing standardization and real-world applications of FHE, such as neural net evaluations, while candidly admitting his own theoretical bent. Looking ahead, Gentry expressed hope for future breakthroughs that could move beyond the current lattice-based blueprint, envisioning *fundamentally new schemes* that might eliminate existing complexities.

---

## 第二部分：FHE的四代发展与性能提升 (10:00 - 20:00)

![Slide 15](images/slide_0015.jpg)

The second-generation schemes introduced ciphertext packing, allowing parallel operations on multiple plaintext slots within a single ciphertext. A key breakthrough was achieving polylogarithmic overhead in the security parameter, which initially seemed optimal. Performance metrics showed thousands of gates processed per second, significantly outpacing Moore's Law, though bootstrapping—a resource-intensive operation—was not initially included in these benchmarks. By 2020, bootstrapping in second-generation schemes like HElib achieved an amortized time of 0.9 milliseconds per plaintext bit, with each ciphertext containing many bits and requiring bootstrapping only every 17 circuit levels.

![Slide 20](images/slide_0020.jpg)

Third-generation schemes improved efficiency and noise management, enabling secure parameters comparable to traditional lattice-based cryptography. Follow-up work further optimized bootstrapping, reducing it to under a tenth of a second by 2016. However, these schemes lacked native support for ciphertext packing, a feature reintroduced in fourth-generation CKKS, which operates on floating-point numbers and is widely adopted for real-world applications like neural networks. *The CKKS scheme really helped FHE immensely* due to its practicality.

![Slide 25](images/slide_0025.jpg)

Chimeric FHE emerged as a hybrid approach, allowing seamless switching between schemes optimized for different data types (e.g., bits vs. floating-point numbers). Recent performance gains include CPU-based bootstrapping at 19 microseconds per bit and GPU-based implementations achieving sub-microsecond speeds.

Applications of FHE span genomic analysis, where competitions drive innovations in privacy-preserving algorithms, and private information retrieval (PIR), which faces inherent efficiency challenges. In genomics, teams have achieved tasks like voice recognition among 100 individuals in under a second. PIR, while theoretically limited by server overhead, benefits from FHE's cryptographic efficiency. *The server has to touch every item in the database*, but advancements mitigate computational costs.

---

## 第三部分：性能优化、可用性与标准化 (20:00 - 30:00)

![Slide 30](images/slide_0030.jpg)

A key development is the significant speed increase in PIR schemes, with one paper achieving a ciphertext expansion ratio of four over nine, making communication bandwidth nearly optimal. Preliminary implementations show PIR queries on a million 30KB files taking 86 seconds, comparable to unaccelerated AES encryption times. Hardware acceleration for FHE is also progressing, with a DARPA program funding efforts to develop accelerators, and recent papers reporting amortized times as low as 0.29 microseconds per bit. *So the amount of time for the server to respond to a PIR query is basically the same as a whole database encryption using AES, which I think is really amazing.*

![Slide 38](images/slide_0038.jpg)

Usability tools like Google's open-source transpiler aim to simplify the translation of high-level code into encrypted data operations, reducing the need for deep crypto expertise. Standardization is advancing through NIST's post-quantum cryptography initiative, where five of seven finalists are lattice-based schemes, indicating FHE's growing role in future cryptographic standards. Workshops are also drafting standards for homomorphic encryption, covering security levels, APIs, and applications. *Lattice based crypto certainly is on its way to being standardized. It's here to stay.*

![Slide 43](images/slide_0043.jpg)

The discussion then shifts to the mathematical foundations of FHE, defining public key encryption and its probabilistic nature, essential for semantic security. Homomorphic encryption introduces an evaluate algorithm, enabling computations on ciphertexts that decrypt to the same result as if operations were performed on plaintexts. This is visualized through commutative diagrams, where the order of decryption and function application doesn't affect the outcome. FHE schemes support families of functions, such as arithmetic circuits, with the ultimate goal of handling all computable functions.

---

## 第四部分：同态加密的两种构造方法 (30:00 - 40:00)

![Slide 48](images/slide_0048.jpg)

### 密码学方法 vs 数学方法

The transcript outlines two primary methods for developing homomorphic encryption schemes. The first, termed *the cryptographic way*, begins with established cryptographic assumptions, constructs public key encryption atop them, and then attempts to introduce homomorphic properties. This approach benefits from inherent security due to its foundation in proven assumptions but may struggle to achieve homomorphism unless the initial scheme coincidentally supports it.

![Slide 52](images/slide_0052.jpg)

The second, *the mathematical way*, starts with homomorphisms—structure-preserving maps between algebraic systems—and later addresses security by masking these structures to achieve semantic security. While this method enables exploration of diverse mathematical frameworks, it risks producing insecure schemes, requiring iterative patching.

### 同态映射与复杂性理论

A homomorphism preserves operations between algebraic structures, illustrated by the example of mapping addition to multiplication via the exponential function. The core idea of homomorphic encryption emerges when these homomorphisms intersect with complexity theory: operations (rightward arrows in a commutative diagram) remain computationally easy, while homomorphisms (downward arrows) become hard without a trapdoor or secret key.

![Slide 57](images/slide_0057.jpg)

### 构造公钥同态加密

The transcript describes a generic method to convert private key homomorphic encryption (supporting modular addition) into public key encryption. The public key consists of multiple encryptions of zero and one, while encryption involves homomorphically adding a random subset of these ciphertexts to produce a new ciphertext encoding the message.

### Legendre符号示例

A hypothetical example using the Legendre symbol demonstrates how mathematical homomorphisms can inspire encryption schemes. The Legendre symbol, a multiplicative homomorphism from integers modulo a prime *p* to {−1, 1}, forms a commutative diagram where decryption applies the symbol. However, *p* must remain secret to prevent trivial decryption.

*The pro of this approach is that it sort of allows you to look at different mathematical structures and consider whether they would be useful for cryptography.*
*The con is, well, your scheme is likely to be broken and then you're one of those people that proposes lots of broken schemes.*

---

## 第五部分：经典方案与量子攻击 (40:00 - 50:00)

![Slide 62](images/slide_0062.jpg)

### Goldwasser-Micali方案

The discussion begins by explaining the Goldwasser-Micali encryption scheme, which hides a prime P using a product n of two primes P and Q, leveraging quadratic residuality for security. The method involves masking the homomorphism with another prime Q to enhance security. The speaker then contrasts this with Rothblum's more generic technique, which uses homomorphism to create semantically secure encryption.

![Slide 67](images/slide_0067.jpg)

### 量子计算的威胁

A significant limitation of these schemes is their vulnerability to quantum attacks. The transcript highlights Shor's algorithm, which can compute the order of a group, making it possible to distinguish between encryptions of zero and other values in homomorphic encryption schemes based on abelian or solvable groups. This vulnerability extends to ring homomorphisms, where encryptions of zero form an ideal within the ciphertext ring, enabling linear algebra attacks. The speaker emphasizes that quantum computing fundamentally undermines these schemes.

![Slide 72](images/slide_0072.jpg)

### 近似GCD假设

The discussion then shifts to potential patches for these vulnerabilities, such as the approximate GCD assumption, which adds noise to messages to hide the secret P. This approach forms the basis for a homomorphic encryption scheme where the secret key is a large integer P, and the public key consists of integers close to multiples of P. *The approximate GCD assumption is that if you sample lots of numbers X that are each very close to multiples of P, but not exact multiples of P, then those integers are indistinguishable from random integers.*

---

## 第六部分：噪声管理与LWE假设 (50:00 - 60:00)

![Slide 76](images/slide_0076.jpg)

### 噪声增长与密文膨胀

The security is based on Rothblum's procedure and the approximate GCD assumption, but two primary issues arise: noise accumulation leading to potential decryption errors and the explosion of ciphertext size as integers are multiplied. The discussion then shifts to a ring homomorphic approach using polynomial evaluation, where the homomorphism evaluates a polynomial at a secret point *S*.

![Slide 80](images/slide_0080.jpg)

### Learning With Errors (LWE)

To address these inefficiencies, the transcript introduces noise and entropy to defeat linear algebra attacks, leading to the learning with errors (LWE) assumption. This assumption posits that linear polynomials evaluating to small values modulo *q* at the secret *s* are indistinguishable from random polynomials. The proposed encryption scheme uses a secret key as a random point and a public key constructed via polynomials that evaluate to small numbers.

![Slide 85](images/slide_0085.jpg)

### 重线性化与自举

Homomorphic addition of ciphertexts preserves the parity of noise, enabling correct decryption. However, multiplying ciphertext polynomials increases their degree, requiring re-linearization techniques to maintain linearity. This involves augmenting the public key with slightly quadratic polynomials to subtract off quadratic terms.

The final challenge addressed is bootstrapping, a method to reduce noise in ciphertexts to prevent decryption errors. The transcript explores using the decryption algorithm itself to refresh ciphertexts, leveraging a commutative diagram to ensure the process preserves the encrypted message. *The errors here are all even, so that when you subtract off these polynomials, you preserve the parity of the error.*

---

## 第七部分：FHE的未来展望 (60:00 - 65:22)

![Slide 91](images/slide_0091.jpg)

### 密文空间的代数结构

The speaker explains that the ciphertext space lacks the original ring structure of the plaintext space, instead forming a *magma*—a minimally structured algebraic system with commutative but non-associative operations. This unstructured nature may be inherent to FHE schemes, as more structured approaches (like solvable groups) have proven vulnerable to quantum attacks.

![Slide 95](images/slide_0095.jpg)

### 挑战与机遇

The analysis highlights challenges with non-solvable groups, such as potential quantum subgroup attacks and issues with linearity. Representation theory has been used to break schemes like Barrington groups, demonstrating the fragility of structured ciphertext spaces. The speaker speculates about alternative approaches, such as leveraging multivariate cryptography to create ciphertext spaces with random-like operations, akin to existing lattice-based schemes.

![Slide 99](images/slide_0099.jpg)

Despite unresolved challenges, the speaker expresses optimism about future breakthroughs in FHE. The discussion underscores the tension between achieving functional homomorphic operations and maintaining cryptographic security, particularly against quantum threats. *It would be cool to have a HFE scheme just for the acronym at least* reflects both the technical aspirations and playful curiosity driving research in this field.
