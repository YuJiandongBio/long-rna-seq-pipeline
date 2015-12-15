#!/usr/bin/env python2.7
# tool_versions.py v1.1  Creates "SW" versions json string for a particular DX applet.
#                        Write request to stdout and verbose info to stderr.  This allows easy use in dx app scripts.

import sys, os, argparse, json, commands

# APP_TOOLS is a dict keyed by applet script name with a list of tools that it uses.
APP_TOOLS = {
    # lrna:    
    "align-star-pe":            [ "lrna-align-star-pe.sh", "STAR", "samtools" ],
    "align-star-se":            [ "lrna-align-star-se.sh", "STAR", "samtools" ],
    "align-tophat-pe":          [ "lrna-align-tophat-pe.sh", "TopHat", "bowtie2", "samtools", "tophat_bam_xsA_tag_fix.pl" ],
    "align-tophat-se":          [ "lrna-align-tophat-se.sh", "TopHat", "bowtie2", "samtools" ],
    "bam-to-bigwig-stranded":   [ "lrna-bam-to-stranded-signals.sh", "STAR","bedGraphToBigWig" ],
    "bam-to-bigwig-unstranded": [ "lrna-bam-to-unstranded-signals.sh", "STAR","bedGraphToBigWig" ],
    "quant-rsem":               [ "lrna-rsem-quantification.sh", "RSEM" ],
    "mad-qc":                   [ "MAD.R" ],

    # srna:    
    "small-rna-prep-star":      [ "srna-index.sh", "STAR", "extract_gene_ids.awk" ], 
    "small-rna-align":          [ "srna-align.sh", "STAR", "samtools" ], 
    "small-rna-signals":        [ "srna-signals.sh", "STAR","bedGraphToBigWig" ], 
    "small-rna-mad-qc":         [ "MAD.R", "extract_gene_ids.awk", "sum_srna_expression.awk" ],

    # rampage:    
    "rampage-align-pe":         [ "ram-align-star-pe.sh", "STAR", "samtools" ],
    "rampage-signals":          [ "ram-signal.sh", "STAR", "bedGraphToBigWig" ],
    "rampage-peaks":            [ "ram-peaks.sh", "call_peaks (grit)", "bedToBigBed", "pigz", "samtools" ],
    "rampage-idr":              [ "ram-idr.sh", "Anaconda3", "idr", "bedToBigBed", "pigz" ],
    "rampage-mad-qc":           [ "MAD.R" ],

    # utility:    
    "merge-annotation":         [ "GTF.awk" ],
    "prep-rsem":                [ "RSEM" ], 
    "prep-star":                [ "STAR" ], 
    "prep-tophat":              [ "TopHat", "bowtie2" ], 
    }
# Virtual apps only differ from their parent by name/version. 
VIRTUAL_APPS = {
    # lrna virtuals:    
    "bam-to-bigwig-stranded-tophat":   "bam-to-bigwig-stranded",
    "bam-to-bigwig-unstranded-tophat": "bam-to-bigwig-unstranded",
    "quant-rsem-alt":                  "quant-rsem",
    "mad-qc-alt":                      "mad-qc",

    }


# ALL_TOOLS contains the printable tool name (key) and the command that is used to determine the version.
ALL_TOOLS = {
            "Anaconda3":                 "ls Anaconda3*.sh | head -1 | cut -d - -f 2",
            "bedGraphToBigWig":          "bedGraphToBigWig 2>&1 | grep 'bedGraphToBigWig v' | awk '{print $2$3}'",
            "bedToBigBed":               "bedToBigBed 2>&1 | grep 'bedToBigBed v' | awk '{print $2$3}'",
            "bowtie2":                   "bowtie2 --version 2>&1 | grep bowtie | awk '{print $3}'",
            "call_peaks (grit)":         "call_peaks --version 2>&1 | grep call_peaks | awk '{print $3}'",
            "GTF.awk":                   "echo unversioned",
            "idr":                       "idr/bin/idr --version 2>&1 | grep IDR | awk '{print $2}'",
            "MAD.R":                     "grep version /usr/bin/MAD.R | awk '{print $3}'",
            "extract_gene_ids.awk":      "grep version /usr/bin/extract_gene_ids.awk | awk '{print $3}'",
            "sum_srna_expression.awk":   "grep version /usr/bin/sum_srna_expression.awk | awk '{print $3}'",
            "RSEM":                      "rsem-calculate-expression --version | awk '{print $4}'",
            "samtools":                  "samtools 2>&1 | grep Version | awk '{print $2}'",
            "STAR":                      "STAR --version | awk '{print $1}' | cut -d _ -f 2-",
            "TopHat":                    "tophat -v | awk '{print $2}'",
            "tophat_bam_xsA_tag_fix.pl": "perl /usr/bin/tophat_bam_xsA_tag_fix.pl --version 2>&1",
            "pigz":                      "pigz --version 2>&1 | awk '{print $2}'",
            "lrna-align-star-pe.sh":             "lrna-align-star-pe.sh | grep usage | awk '{print $2}' | tr -d :",
            "lrna-align-star-se.sh":             "lrna-align-star-se.sh | grep usage | awk '{print $2}' | tr -d :",
            "lrna-align-tophat-pe.sh":           "lrna-align-tophat-pe.sh | grep usage | awk '{print $2}' | tr -d :",
            "lrna-align-tophat-se.sh":           "lrna-align-tophat-se.sh | grep usage | awk '{print $2}' | tr -d :",
            "lrna-bam-to-stranded-signals.sh":   "lrna-bam-to-stranded-signals.sh | grep usage | awk '{print $2}' | tr -d :",
            "lrna-bam-to-unstranded-signals.sh": "lrna-bam-to-unstranded-signals.sh | grep usage | awk '{print $2}' | tr -d :",
            "lrna-rsem-quantification.sh":       "lrna-rsem-quantification.sh | grep usage | awk '{print $2}' | tr -d :",
            "ram-align-star-pe.sh":     "ram-align-star-pe.sh | grep usage | awk '{print $2}' | tr -d :",
            "ram-signal.sh":            "ram-signal.sh | grep usage | awk '{print $2}' | tr -d :",
            "ram-peaks.sh":             "ram-peaks.sh | grep usage | awk '{print $2}' | tr -d :",
            "ram-idr.sh":               "ram-idr.sh | grep usage | awk '{print $2}' | tr -d :",
            "srna-index.sh":            "srna-index.sh | grep usage | awk '{print $2}' | tr -d :",
            "srna-align.sh":            "srna-align.sh | grep usage | awk '{print $2}' | tr -d :",
            "srna-signals.sh":          "srna-signals.sh | grep usage | awk '{print $2}' | tr -d :",
            }

def parse_dxjson(dxjson):
    '''Parses the dnanexus-executable.json file in the job directory to get applet name and version.'''
    with open(dxjson) as data_file:    
        dxapp = json.load(data_file)

    appver = "unknown"    
    applet = dxapp.get("name").split()[0]
    if "version" in dxapp:
        appver = dxapp.get("version")
    else:
        title = dxapp.get("title")
        last_word = title.split(' ')[-1]
        if last_word.startswith('(virtual-') and last_word.endswith(')'):
            appver = last_word[9:-1]
        elif last_word.startswith('(v') and last_word.endswith(')'):
            appver = last_word[2:-1]
    
    return (applet, appver)


def main():
    parser = argparse.ArgumentParser(description =  "Versions parser for a dx applet. " + \
                                                    "Prints version lines to stderr and json string to stdout. " + \
                                                    "MUST specify either --applet and --appver or --dxjson.")
    parser.add_argument('-a','--applet', required=False,
                        help="Applet to print versions for")
    parser.add_argument('-av','--appver', required=False,
                        help="Version of applet")
    parser.add_argument('-j','--dxjson', required=False,
                        help="Use dnanexus json file to discover 'applet' and 'appver'")
    parser.add_argument('-q', '--quiet', action="store_true", required=False, default=False, 
                        help="Don't print versions to stderr.")
    parser.add_argument('-v', '--verbose', action="store_true", required=False, default=False, 
                        help="Show the command-line that is used to get the version.")


    args = parser.parse_args(sys.argv[1:])
    if len(sys.argv) < 3:
        parser.print_usage()
        return
        
    if (args.applet == None or args.appver == None) and args.dxjson == None:
        parser.print_help()
        return

    applet = args.applet
    applet = args.appver
    
    if args.dxjson != None:
        (applet,appver) = parse_dxjson(args.dxjson)
    
    versions = {}
    versions["DX applet"] = { applet: appver }
    if not args.quiet:
        sys.stderr.write("********\n")
        sys.stderr.write("* Running " + applet + ": " + appver+ "\n")
    
    if applet in VIRTUAL_APPS:
        tools = APP_TOOLS[VIRTUAL_APPS[applet]]
    else:
        tools = APP_TOOLS[applet]
    for tool in tools:
        cmd = ALL_TOOLS[tool]
        if args.verbose:
            sys.stderr.write("cmd> " + cmd + "\n")
        err, ver = commands.getstatusoutput(cmd)
        versions[tool] = ver
        if not args.quiet:
            sys.stderr.write("* " + tool + " version: " + ver + "\n")

    if not args.quiet:
        sys.stderr.write("********\n")
    
    print json.dumps(versions) 
     
if __name__ == '__main__':
    main()


