#!/usr/local/bin/perl
# Show a form for validating multiple servers

require './virtual-server-lib.pl';
&can_edit_templates() || &error($text{'newvalidate_ecannot'});
&ui_print_header(undef, $text{'newvalidate_title'}, "", "newvalidate");

# Start of tabs
print &ui_tabs_start([ [ 'val', $text{'newvalidate_tabval'} ],
		       [ 'sched', $text{'newvalidate_tabsched'} ] ],
		     'mode', $in{'mode'} || 'val', 1);

# Start of validation form
print &ui_tabs_start_tab('mode', 'val');
print "$text{'newvalidate_desc'}<p>\n";
print &ui_form_start("validate.cgi", "post");
print &ui_table_start($text{'newvalidate_header'}, undef, 2);

# Servers to check
@doms = &list_domains();
print &ui_table_row($text{'newvalidate_servers'},
		    &ui_radio("servers_def", 1,
			[ [ 1, $text{'newips_all'} ],
			  [ 0, $text{'newips_sel'} ] ])."<br>\n".
		    &servers_input("servers", [ ], \@doms));

# Features to check
foreach $f (@validate_features) {
	push(@fopts, [ $f, $text{'feature_'.$f} ]);
	}
foreach $f (&list_feature_plugins()) {
	if (&plugin_defined($f, "feature_validate")) {
		push(@fopts, [ $f, &plugin_call($f, "feature_name") ]);
		}
	}
print &ui_table_row($text{'newvalidate_feats'},
		    &ui_radio("features_def", 1,
			[ [ 1, $text{'newvalidate_all'} ],
			  [ 0, $text{'newvalidate_sel'} ] ])."<br>\n".
		    &ui_select("features", undef,
			       \@fopts, 10, 1));

print &ui_table_end();
print &ui_form_end([ [ "ok", $text{'newvalidate_ok'} ] ]);
print &ui_tabs_end_tab('mode', 'val');

# Start of scheduled check form
print &ui_tabs_start_tab('mode', 'sched');
print "$text{'newvalidate_desc2'}<p>\n";
print &ui_form_start("save_validate.cgi", "post");
print &ui_table_start($text{'newvalidate_header2'}, undef, 2);

# When to validate
$job = &find_validate_job();
print &ui_table_row($text{'newvalidate_sched'},
	&virtualmin_ui_show_cron_time("sched", $job,
				      $text{'newquotas_whenno'}));

# Who to notify
print &ui_table_row($text{'newvalidate_email'},
	&ui_textbox("email", $config{'validate_email'}, 40));

# Also check config?
print &ui_table_row($text{'newvalidate_config'},
	&ui_yesno_radio("config", $config{'validate_config'}));

# Always email
print &ui_table_row($text{'newvalidate_always'},
	&ui_yesno_radio("always", $config{'validate_always'}));

# Servers to check
@ids = split(/\s+/, $config{'validate_servers'});
print &ui_table_row($text{'newvalidate_servers'},
		    &ui_radio("servers_def", 1,
			[ [ 1, $text{'newips_all'} ],
			  [ 0, $text{'newips_sel'} ] ])."<br>\n".
		    &servers_input("servers", \@ids, \@doms));

# Features to check
@fids = split(/\s+/, $config{'validate_features'});
print &ui_table_row($text{'newvalidate_feats'},
		    &ui_radio("features_def", 1,
			[ [ 1, $text{'newvalidate_all'} ],
			  [ 0, $text{'newvalidate_sel'} ] ])."<br>\n".
		    &ui_select("features", \@fids,
			       \@fopts, 10, 1));

print &ui_table_end();
print &ui_form_end([ [ undef, $text{'save'} ] ]);

print &ui_tabs_end_tab('mode', 'sched');

print &ui_tabs_end();

&ui_print_footer("", $text{'index_return'});
