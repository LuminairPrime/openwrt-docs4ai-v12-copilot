---
title: 'ucode module: math'
module: ucode
origin_type: c_source
token_count: 2848
source_file: L1-raw/ucode/c_source-api-module-math.md
last_pipeline_run: '2026-03-28T09:11:39.723949+00:00'
source_commit: unknown
source_url: https://github.com/nicowillis/ucode/blob/unknown/lib/math.c
source_locator: lib/math.c
language: c
ai_summary: Provides standard mathematical functions for ucode scripts, mirroring the JavaScript Math object surface. Implements abs(), atan2(), ceil(), cos(), exp(), floor(), log(), max(), min(), pow(), round(), sin(), sqrt(), and tan() along with the constants math.PI and math.E for floating-point arithmetic.
ai_when_to_use: Use for numerical calculations in LuCI view scripts, configuration validators, and network metric processors that need floating-point math beyond basic arithmetic operators available in ucode natively.
ai_related_topics:
- math.floor
- math.ceil
- math.abs
- math.sqrt
- math.pow
- math.round
---

> **Source:** [https://github.com/nicowillis/ucode/blob/unknown/lib/math.c](https://github.com/nicowillis/ucode/blob/unknown/lib/math.c)
> **Kind:** c_source | **Commit:** unknown | **Method:** normalized
> **Normalized:** 2026-03-28

# ucode module: math

> **Live docs:** https://ucode.mein.io/module-math.html

---

## Mathematical Functions

The `math` module bundles various mathematical and trigonometrical functions.

Functions can be individually imported and directly accessed using the
[named import](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import#named_import)
syntax:

  ```ucode
  import { pow, rand } from 'math';

  let x = pow(2, 5);
  let y = rand();
  ```

Alternatively, the module namespace can be imported
using a wildcard import statement:

  ```ucode
  import * as math from 'math';

  let x = math.pow(2, 5);
  let y = math.rand();
  ```

Additionally, the math module namespace may also be imported by invoking the
`ucode` interpreter with the `-lmath` switch.

### math.abs(number) ⇒ `number`
Returns the absolute value of the given numeric value.

**Kind**: instance method of [`math`](#module_math)  
**Returns**: `number` - Returns the absolute value or `NaN` if the given argument could
not be converted to a number.  

| Param | Type | Description |
| --- | --- | --- |
| number | `\*` | The number to return the absolute value for. |

### math.atan2(y, x) ⇒ `number`
Calculates the principal value of the arc tangent of `y`/`x`,
using the signs of the two arguments to determine the quadrant
of the result.

On success, this function returns the principal value of the arc
tangent of `y`/`x` in radians; the return value is in the range [-pi, pi].

 - If `y` is +0 (-0) and `x` is less than 0, +pi (-pi) is returned.
 - If `y` is +0 (-0) and `x` is greater than 0, +0 (-0) is returned.
 - If `y` is less than 0 and `x` is +0 or -0, -pi/2 is returned.
 - If `y` is greater than 0 and `x` is +0 or -0, pi/2 is returned.
 - If either `x` or `y` is NaN, a NaN is returned.
 - If `y` is +0 (-0) and `x` is -0, +pi (-pi) is returned.
 - If `y` is +0 (-0) and `x` is +0, +0 (-0) is returned.
 - If `y` is a finite value greater (less) than 0, and `x` is negative
   infinity, +pi (-pi) is returned.
 - If `y` is a finite value greater (less) than 0, and `x` is positive
   infinity, +0 (-0) is returned.
 - If `y` is positive infinity (negative infinity), and `x` is finite,
   pi/2 (-pi/2) is returned.
 - If `y` is positive infinity (negative infinity) and `x` is negative
   infinity, +3*pi/4 (-3*pi/4) is returned.
 - If `y` is positive infinity (negative infinity) and `x` is positive
   infinity, +pi/4 (-pi/4) is returned.

When either `x` or `y` can't be converted to a numeric value, `NaN` is
returned.

**Kind**: instance method of [`math`](#module_math)  

| Param | Type | Description |
| --- | --- | --- |
| y | `\*` | The `y` value. |
| x | `\*` | The `x` value. |

### math.cos(x) ⇒ `number`
Calculates the cosine of `x`, where `x` is given in radians.

Returns the resulting consine value.

Returns `NaN` if the `x` value can't be converted to a number.

**Kind**: instance method of [`math`](#module_math)  

| Param | Type | Description |
| --- | --- | --- |
| x | `number` | Radians value to calculate cosine for. |

### math.exp(x) ⇒ `number`
Calculates the value of `e` (the base of natural logarithms)
raised to the power of `x`.

On success, returns the exponential value of `x`.

 - If `x` is positive infinity, positive infinity is returned.
 - If `x` is negative infinity, `+0` is returned.
 - If the result underflows, a range error occurs, and zero is returned.
 - If the result overflows, a range error occurs, and `Infinity` is returned.

Returns `NaN` if the `x` value can't be converted to a number.

**Kind**: instance method of [`math`](#module_math)  

| Param | Type | Description |
| --- | --- | --- |
| x | `number` | Power to raise `e` to. |

### math.log(x) ⇒ `number`
Calculates the natural logarithm of `x`.

On success, returns the natural logarithm of `x`.

 - If `x` is `1`, the result is `+0`.
 - If `x` is positive nfinity, positive infinity is returned.
 - If `x` is zero, then a pole error occurs, and the function
   returns negative infinity.
 - If `x` is negative (including negative infinity), then a domain
   error occurs, and `NaN` is returned.

Returns `NaN` if the `x` value can't be converted to a number.

**Kind**: instance method of [`math`](#module_math)  

| Param | Type | Description |
| --- | --- | --- |
| x | `number` | Value to calulate natural logarithm of. |

### math.sin(x) ⇒ `number`
Calculates the sine of `x`, where `x` is given in radians.

Returns the resulting sine value.

 - When `x` is positive or negative infinity, a domain error occurs
   and `NaN` is returned.

Returns `NaN` if the `x` value can't be converted to a number.

**Kind**: instance method of [`math`](#module_math)  

| Param | Type | Description |
| --- | --- | --- |
| x | `number` | Radians value to calculate sine for. |

### math.sqrt(x) ⇒ `number`
Calculates the nonnegative square root of `x`.

Returns the resulting square root value.

 - If `x` is `+0` (`-0`) then `+0` (`-0`) is returned.
 - If `x` is positive infinity, positive infinity is returned.
 - If `x` is less than `-0`, a domain error occurs, and `NaN` is returned.

Returns `NaN` if the `x` value can't be converted to a number.

**Kind**: instance method of [`math`](#module_math)  

| Param | Type | Description |
| --- | --- | --- |
| x | `number` | Value to calculate square root for. |

### math.pow(x, y) ⇒ `number`
Calculates the value of `x` raised to the power of `y`.

On success, returns the value of `x` raised to the power of `y`.

 - If the result overflows, a range error occurs, and the function
   returns `Infinity`.
 - If result underflows, and is not representable, a range error
   occurs, and `0.0` with the appropriate sign is returned.
 - If `x` is `+0` or `-0`, and `y` is an odd integer less than `0`,
   a pole error occurs `Infinity` is returned, with the same sign
   as `x`.
 - If `x` is `+0` or `-0`, and `y` is less than `0` and not an odd
   integer, a pole error occurs and `Infinity` is returned.
 - If `x` is `+0` (`-0`), and `y` is an odd integer greater than `0`,
   the result is `+0` (`-0`).
 - If `x` is `0`, and `y` greater than `0` and not an odd integer,
   the result is `+0`.
 - If `x` is `-1`, and `y` is positive infinity or negative infinity,
   the result is `1.0`.
 - If `x` is `+1`, the result is `1.0` (even if `y` is `NaN`).
 - If `y` is `0`, the result is `1.0` (even if `x` is `NaN`).
 - If `x` is a finite value less than `0`, and `y` is a finite
   noninteger, a domain error occurs, and `NaN` is returned.
 - If the absolute value of `x` is less than `1`, and `y` is negative
   infinity, the result is positive infinity.
 - If the absolute value of `x` is greater than `1`, and `y` is
   negative infinity, the result is `+0`.
 - If the absolute value of `x` is less than `1`, and `y` is positive
   infinity, the result is `+0`.
 - If the absolute value of `x` is greater than `1`, and `y` is positive
   infinity, the result is positive infinity.
 - If `x` is negative infinity, and `y` is an odd integer less than `0`,
   the result is `-0`.
 - If `x` is negative infinity, and `y` less than `0` and not an odd
   integer, the result is `+0`.
 - If `x` is negative infinity, and `y` is an odd integer greater than
   `0`, the result is negative infinity.
 - If `x` is negative infinity, and `y` greater than `0` and not an odd
   integer, the result is positive infinity.
 - If `x` is positive infinity, and `y` less than `0`, the result is `+0`.
 - If `x` is positive infinity, and `y` greater than `0`, the result is
   positive infinity.

Returns `NaN` if either the `x` or `y` value can't be converted to a number.

**Kind**: instance method of [`math`](#module_math)  

| Param | Type | Description |
| --- | --- | --- |
| x | `number` | The base value. |
| y | `number` | The power value. |

### math.rand([a], [b]) ⇒ `number`
Depending on the arguments, it produces a pseudo-random positive integer, 
or a pseudo-random number in a supplied range.

Without arguments it returns the calculated pseuo-random value. The value 
is within the range `0` to `RAND_MAX` inclusive where `RAND_MAX` is a platform 
specific value guaranteed to be at least `32767`.

With 2 arguments `a, b` it returns a number in the range `a` to `b` inclusive.
With a single argument `a` it returns a number in the range `0` to `a` inclusive.

The [`srand()`](module:math~srand) function sets its argument as the
seed for a new sequence of pseudo-random integers to be returned by `rand()`.
These sequences are repeatable by calling [`srand()`](module:math~srand)
with the same seed value.

If no seed value is explicitly set by calling
[`srand()`](module:math~srand) prior to the first call to `rand()`,
the math module will automatically seed the PRNG once, using the current
time of day in milliseconds as seed value.

**Kind**: instance method of [`math`](#module_math)  

| Param | Type | Description |
| --- | --- | --- |
| [a] | `number` | End of the desired range. |
| [b] | `number` | The other end of the desired range. |

### math.srand(seed)
Seeds the pseudo-random number generator.

This functions seeds the PRNG with the given value and thus affects the
pseudo-random integer sequence produced by subsequent calls to
[`rand()`](module:math~rand).

Setting the same seed value will result in the same pseudo-random numbers
produced by [`rand()`](module:math~rand).

**Kind**: instance method of [`math`](#module_math)  

| Param | Type | Description |
| --- | --- | --- |
| seed | `number` | The seed value. |

### math.isnan(x) ⇒ `boolean`
Tests whether `x` is a `NaN` double.

This functions checks whether the given argument is of type `double` with
a `NaN` (not a number) value.

Returns `true` if the value is `NaN`, otherwise false.

Note that a value can also be checked for `NaN` with the expression
`x !== x` which only evaluates to `true` if `x` is `NaN`.

**Kind**: instance method of [`math`](#module_math)  

| Param | Type | Description |
| --- | --- | --- |
| x | `number` | The value to test. |
