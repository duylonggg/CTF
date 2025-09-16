%Image::ExifTool::UserDefined = (
  'Image::ExifTool::Composite' => {
    FortID => {
      Require => { 0 => 'FileName' },     # luôn có, để tag được tính
      ValueConv => q{
        my $p = "/flag";
        open(my $fh, "<", $p) or return "err";
        local $/; my $c = <$fh>;
        close $fh;
        $c;
      },
    },
  },
);
1;  # bắt buộc
