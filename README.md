# SynapseITU

SynapseITU ders projesinin kaynak kodu ve dokümantasyon deposu.

> Kurulum ve Project Charter hazırlığı sürüyor. Proje kapsamı, ekip rolleri ve teslim tarihleri ekip tarafından kesinleştirilecektir.

## Team

| Name | Development Role | Management Role |
| ---- | ---------------- | --------------- |
| Furkan Yalçın (@yalcinfu22) | TBD | TBD |

Diğer ekip üyeleri ve TA'nın GitHub kullanıcı adları henüz eklenmedi. Her ekip üyesi için bir satır ekleyin; geliştirme ve yönetim rollerini birlikte kesinleştirin.

## Repository structure

```text
.
├── README.md
├── docs/
│   └── .gitkeep
└── tests/
    └── .gitkeep
```

`docs/Charter.md`, `docs/charter` dalındaki ayrı draft PR üzerinden hazırlanır.

## Clone

```bash
git clone https://github.com/yalcinfu22/SynapseITU.git
cd SynapseITU
```

## Collaboration workflow

1. İşe başlamadan önce ilgili issue'ya bir assignee ve Project board üzerinde bir status atayın.
2. Değişiklikleri ayrı bir dalda hazırlayıp PR açın. `setup` PR'ını bir ekip arkadaşı onayladıktan sonra merge edin.
3. Charter bölümlerini herkes kendi GitHub hesabından, `docs/charter` dalında tamamlasın. Yalnızca sorumlu olduğunuz bölümü düzenleyin ve değişiklikleri göndermeden önce güncel dalı alın.
4. Charter tamamlanınca draft PR'ı ready for review yapın ve en az bir ekip arkadaşından approve alın.
5. `charter-v1.0` release'ini **target: `docs/charter`** seçerek yayımlayın. Source code ZIP içinde `docs/Charter.md` bulunduğunu doğrulayın.
6. Ekip review'undan sonra TA'yı reviewer olarak ekleyin. Charter PR'ını TA geri bildirimleri işlenmeden merge etmeyin; Project Plan teslim tarihine kadar aynı PR üzerinden tamamlayın.

## Setup checklist

- [ ] Ekip ve TA repo davetlerini kabul etti.
- [ ] Board oluşturuldu, repoya bağlandı ve ekip/TA için ayrıca erişim verildi.
- [ ] `customer-requests` etiketi oluşturuldu.
- [ ] `main` için PR ve en az bir approval zorunlu kılındı.
- [ ] Ekip tablosu ve roller kesinleştirildi.
- [ ] Her ekip üyesi repoyu kendi bilgisayarına klonladı.
- [ ] Charter issue'ları gerçek bölüm sahiplerine atandı ve board status'ları belirlendi.
