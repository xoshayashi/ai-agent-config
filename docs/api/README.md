# API 仕様書 & インテグレーション (API & SDK Integration Docs)

このディレクトリは、内部・外部システム向けの API エンドポイント、gRPC 定義、および SDK の利用方法に関するドキュメントを管理するための場所です。

## 📁 今後のドキュメント追加予定
プロジェクトの成長に伴い、以下のような技術リファレンスドキュメントが追加されます。

- **`endpoints_specification.md`**: REST API のエンドポイント一覧、リクエスト・レスポンススキーマ、ステータスコード定義。
- **`grpc_protobuf_definitions.md`**: gRPC通信用の `.proto` ファイル構造、サービス定義、ストリーミング要件。
- **`sdk_usage_guide.md`**: Python / TypeScript などの各言語向けクライアントライブラリ（SDK）の実装例。
- **`authentication_reference.md`**: APIへのアクセス認証（OAuth2.0, Bearer Token, API Key）の方法。

## ⚙️ インテグレーション設計
1. **スキーマ駆動開発 (Schema-Driven)**: APIのインターフェースは OpenAPI 3.0 または Protocol Buffers によって厳格にスキーマを定義し、型セーフなコード生成を行います。
2. **下位互換性の維持**: APIの破壊的変更を伴うアップデートを行う際は、バージョン管理（`/v1/`, `/v2/`等）を明確に行い、古いバージョンを段階的に非推奨（Deprecation）にします。
