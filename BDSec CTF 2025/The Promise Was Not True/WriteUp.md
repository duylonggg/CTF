# Write Up

Phân tích "Phép Thuật"

Bạn có một câu đố CTF (Capture The Flag) rất thú vị với một dòng chữ bí ẩn được gọi là "phép thuật": [$1=$[\%1\]?~[$1-f;!*]?]f: 10f;!. và yêu cầu tìm một mật mã gồm 7 chữ số. Gợi ý quan trọng nhất là "You already have everything you need" (Bạn đã có mọi thứ bạn cần).

Thoạt nhìn, dòng chữ này trông giống một ngôn ngữ lập trình "khó hiểu" (esoteric language) như Brainfk, nhưng với các ký tự $, %, f: thì nó không phải Brainfk chuẩn. Đây là một chiêu thường thấy trong CTF: đánh lừa bạn rằng nó là một ngôn ngữ phức tạp, nhưng thực ra nó ẩn chứa một phép toán đơn giản.

Tìm manh mối
Gợi ý "Bạn đã có mọi thứ bạn cần" luôn ám chỉ rằng đáp án nằm ngay trong dữ liệu bạn đang có – tức là chính dòng "phép thuật" đó.

Hãy nhìn kỹ lại dòng chữ: [$1=$[\%1\]?~[$1-f;!*]?]f: **10f;!.**

Trong một chuỗi ký tự dài và có vẻ phức tạp như vậy, nếu có các con số rõ ràng xuất hiện, chúng thường là manh mối quan trọng nhất. Ở đây, ta thấy ngay số 10.

Tiếp theo, hãy để ý các ký tự đặc biệt ở cuối dòng: **f;!.**.

Ký tự ! (dấu chấm than) là một ký hiệu toán học rất phổ biến, đại diện cho giai thừa (factorial). Ví dụ, 5!=5×4×3×2×1.

Ký tự f; có thể là "nhiễu" (noise) để làm khó người giải, hoặc là một cách viết tắt của "function" (hàm), ám chỉ rằng ký tự tiếp theo là một phép toán áp dụng cho số đứng trước.

Giải mã mật mã
Nếu ta kết hợp số 10 và ký hiệu ! (giai thừa) lại với nhau, ta sẽ có phép toán: 10!

Hãy tính toán giá trị của 10!:

10!=10×9×8×7×6×5×4×3×2×1
10!=3,628,800

Và đây chính là điểm mấu chốt: 3,628,800 là một số có 7 chữ số! Điều này hoàn toàn khớp với yêu cầu của đề bài là tìm một mật mã gồm 7 chữ số.

Các ký tự khác trong dòng chữ ($, [, ], ?, ~, -, *, %) có thể chỉ là để tạo ra sự bí ẩn, đánh lạc hướng người giải, hoặc chúng thuộc về một "ngôn ngữ phép thuật" không cần thiết phải giải mã toàn bộ trong bối cảnh này.

Kết luận
Mật mã chính là kết quả của 10!.

Mật mã: 3628800

Để nộp đáp án theo định dạng yêu cầu của CTF (BDSEC{passCode}), bạn sẽ viết:

BDSEC{3628800}
