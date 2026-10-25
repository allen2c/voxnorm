# 0001-customer-service-phone-forms

**Date**: 2026-10-21 · **Against**: voxnorm 0.2.0 (8c816e8) · **Status**: decided, shipped in 0.2.1 (22f29f1)

## Question

A zh-TW customer-service sentence fed to TTS misread its phone numbers, national ID and
transaction serial. Which of those are scanner gaps the charter allows us to
close, and which belong to the caller?

```
您好，這裡是AI智能服務，您的身分證字號是A123456789，登記的手機號碼是0912345678，
email信箱是a12345.user@example.com.tw。本次交易金額為新臺幣12345元，交易序號是12345678901。
系統已發送 OTP 驗證碼，請確認您的Account狀態。如需進一步協助，請於早上8:00到下午5:00
撥打(02)123-4567或(02)1234-5678，謝謝。
```

## Setup

`normalize()` on the sentence above and on ~40 variants of each form
(spacing, full-width parentheses, `+886`, extensions, masked card tails,
SSML tags), in zh and forced en. The cases now live as unit tests in
`tests/test_zh.py` (`test_phone_shapes`, `test_customer_service_sentence`,
…) and `tests/test_en.py`.

## Method

Each form was judged by the charter: does its shape alone settle the
reading? A form two readings share stays written; a form only vocabulary
can settle goes to `code_words`.

## Findings

| Finding | Input → actual (0.2.0) | Expected | Class |
| --- | --- | --- | --- |
| `parenthesized-area-code` | `(02)1234-5678` → `(零二)1234-5678` | `零二一二三四五六七八` | new form |
| `bare-four-four-group` | `撥打 1234-5678` → stays written | stays written; `code_words=["撥打"]` licenses it | caller |
| `national-id` | `A123456789` → `A一二三…九` | already right since 0.2.0 (`alnum`) | — |
| `long-ungrouped-serial` | `12345678901` → `一百二十三億…` | quantity by default; `code_words=["序號是"]` | caller |
| `plus-country-code` | `+886 912 345 678` → four cardinals | `加八八六九一二…` | bug |
| `extension-hash` | `02-1234-5678#123` → `…#一百二十三` | `…轉一二三` | new form |
| `four-six-grouping` | `0912-345678` → stays written | `零九一二三四五六七八` | new form |
| `masked-tail` | `****1234` → `****一千兩百…` | `****一二三四` | new form |
| `ssml-attribute-digits` | `<break time="500ms"/>` → `五百ms` inside the tag | tag untouched | bug |
| `year-range-half-conversion` | `1990-2000年` → `1990-二零零零年` | stays written | charter violation |

Checked and fine: the email `a12345.user@example.com.tw` stays whole;
`[故作輕鬆]` bracket tags pass through; `0800-092-000` already worked;
`4111-1111-1111-1111` stays written.

## Decision

Shipped in 0.2.1: the phone shapes (parentheses, 6-8 digit group, `+`,
`#`/轉 extension), `code_words` accepting hyphen groups, masked tails, the
`markup` kind, and the year/room lookbehind fix.

Not changed, by charter: a bare `1234-5678` is the same string as the year
range `1990-2000`, and an ungrouped 11-digit run is the same string as an
ungrouped `1500000000元` budget. Both are vocabulary, so `code_words`.
