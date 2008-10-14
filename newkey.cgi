#!/usr/local/bin/perl
# newkey.cgi
# Install a new SSL cert and key

require './virtual-server-lib.pl';
&ReadParseMime();
$d = &get_domain($in{'dom'});
&can_edit_domain($d) && &can_edit_ssl() || &error($text{'edit_ecannot'});

# Validate inputs
&error_setup($text{'newkey_err'});
$cert = $in{'cert'} || $in{'certupload'};
$newkey = $in{'newkey'} || $in{'newkeyupload'};
$cert =~ /BEGIN CERTIFICATE/ &&
  $cert =~ /END CERTIFICATE/ || &error($text{'newkey_ecert'});
$newkey =~ /BEGIN RSA PRIVATE KEY/ &&
  $newkey =~ /END RSA PRIVATE KEY/ || &error($text{'newkey_enewkey'});
$cert =~ s/\r//g;
$newkey =~ s/\r//g;

# Check if a passphrase is needed
$passok = &check_passphrase($newkey, $in{'pass_def'} ? undef : $in{'pass'});
$passok || &error($text{'newkey_epass'});

&ui_print_header(&domain_in($d), $text{'newkey_title'}, "");

# Make sure Apache is setup to use the right key files
&require_apache();
$conf = &apache::get_config();
($virt, $vconf) = &get_apache_virtual($d->{'dom'},
                                      $d->{'web_sslport'});

$d->{'ssl_cert'} ||= &default_certificate_file($d, 'cert');
$d->{'ssl_key'} ||= &default_certificate_file($d, 'key');
&lock_file($virt->{'file'});
&apache::save_directive("SSLCertificateFile", [ $d->{'ssl_cert'} ],
			$vconf, $conf);
&apache::save_directive("SSLCertificateKeyFile", [ $d->{'ssl_key'} ],
			$vconf, $conf);
&flush_file_lines($virt->{'file'});
&unlock_file($virt->{'file'});

# If a passphrase is needed, add it to the top-level Apache config. This is
# done by creating a small script that outputs the passphrase
$pass_script = "$ssl_passphrase_dir/$d->{'id'}";
&lock_file($pass_script);
@pps = &apache::find_directive("SSLPassPhraseDialog", $conf);
@pps_str = &apache::find_directive_struct("SSLPassPhraseDialog", $conf);
&lock_file(@pps_str ? $pps_str[0]->{'file'} : $conf->[0]->{'file'});
($pps) = grep { $_ eq "exec:$pass_script" } @pps;
if ($passok == 2) {
	# Create script, add to Apache config
	if (!-d $ssl_passphrase_dir) {
		&make_dir($ssl_passphrase_dir, 0700);
		}
	&open_tempfile(SCRIPT, ">$pass_script");
	&print_tempfile(SCRIPT, "#!/bin/sh\n");
	&print_tempfile(SCRIPT, "echo ".quotemeta($in{'pass'})."\n");
	&close_tempfile(SCRIPT);
	&set_ownership_permissions(undef, undef, 0700, $pass_script);
	push(@pps, "exec:$pass_script");
	$d->{'ssl_pass'} = $in{'pass'};
	}
else {
	# Remove script and from Apache config
	if ($pps) {
		@pps = grep { $_ ne $pps } @pps;
		}
	delete($d->{'ssl_pass'});
	&unlink_file($pass_script);
	}
&lock_file(@pps_str ? $pps_str[0]->{'file'} : $conf->[0]->{'file'});
&apache::save_directive("SSLPassPhraseDialog", \@pps, $conf, $conf);
&flush_file_lines();

# Save the cert and private keys
&$first_print($text{'newkey_saving'});
&lock_file($d->{'ssl_cert'});
&unlink_file($d->{'ssl_cert'});
&open_tempfile(CERT, ">$d->{'ssl_cert'}");
&print_tempfile(CERT, $cert);
&close_tempfile(CERT);
&set_certificate_permissions($d, $d->{'ssl_cert'});
&unlock_file($d->{'ssl_cert'});

&lock_file($d->{'ssl_key'});
&unlink_file($d->{'ssl_key'});
&open_tempfile(CERT, ">$d->{'ssl_key'}");
&print_tempfile(CERT, $newkey);
&close_tempfile(CERT);
&set_certificate_permissions($d, $d->{'ssl_key'});
&unlock_file($d->{'ssl_key'});
&$second_print($text{'setup_done'});

# Remove the new private key we just installed
if ($d->{'ssl_newkey'}) {
	$newkeyfile = &read_file_contents($d->{'ssl_newkey'});
	if ($newkeyfile eq $newkey) {
		&unlink_logged($d->{'ssl_newkey'});
		delete($d->{'ssl_newkey'});
		delete($d->{'ssl_csr'});
		&save_domain($d);
		}
	}

# Re-start Apache
&register_post_action(\&restart_apache, 1);
&run_post_actions();
&webmin_log("newkey", "domain", $d->{'dom'}, $d);

&ui_print_footer("cert_form.cgi?dom=$in{'dom'}", $text{'cert_return'},
	 	 &domain_footer_link($d),
		 "", $text{'index_return'});

