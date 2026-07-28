# 현재 API 계약

## `GET /health`

애플리케이션의 상태를 확인한다.

- 요청 본문: 없음
- 성공 상태 코드: `200 OK`
- 성공 응답:

```json
{
  "status": "ok"
}
```

- 지원하지 않는 HTTP 메서드: `405 Method Not Allowed`
