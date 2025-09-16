workspace "GNSS processing with AutoBernese" {

    # Default: flat
    !identifiers hierarchical

    model "AutoBernese" {

        external_data_sources = softwareSystem "External data sources" {
            container "TU Wien" "Troposphere-delay model data" "HTTP-server"
            container "AIUB" "Bernese configuration and model data as well as CODE data products" "FTP-server"
            container "Chalmers" "Ocean-loading-tide data" "Web form and email"
        }

        group "Danish Agency for Climate Data" {
            user = person "Geodesist"

            autobernese = softwareSystem "AutoBernese" {

                # Layer: I/O
                cli = container "CLI application" {}

                configuration = container "Configuration" {
                    constructors = component "YAML constructors"
                }

                # Layer: API
                bsw = container "BSW API" {
                    bpe_perl_script = component "BPE program" "Perl script that starts the Bernese Processing Engine" "Perl"
                    bpe_process_runner = component "BPE process runner" "Creates subprocess with a call to the BPE interface"
                    campaign_manager = component "Create, run and inspect BSW campaigns"
                }

                data_transfer = container "Data transfer" {
                    downloader = component "Downloader" "Downloads specified files from external data sources." "FTP/HTTP"
                    download_controller = component "Download controller" "Specifies source files and local destinations."
                }

                preprocessor = container "Preprocess and organise input to and output from BSW" {
                    qaqc = component "Kvalitetssikring [QA] og kvalitetskontrol [QC]" {}
                    sitelog2sta = component "Legacy converter" "Converts sitelogs to station file." "Perl"
                    sitelog2sta_runner = component "sitelog2sta runner" "Creates subprocess with a call to the Perl program"
                }
            }

            file_system = softwareSystem "File system" {
                campaign = container "CAMPAIGN" "BSW campaign workspace"
                datapool = container "DATAPOOL" "BSW raw-data storage"
                savedisk = container "SAVEDISK" "BSW end-product storage"
                everything_else = container "All other data" "The rest of the file system used for GNSS-related data."
            }

            bsw = softwareSystem "BSW" {
                perl_api = container "Perl API" "BSW Perl modules that used to run individual Bernese programs or the Bernese Processing Engine"
                model_data = container "MODEL" "BSW internal model data storage"
                config_data = container "CONFIG" "BSW internal configuration data storage"
            }

        }

        # Relationships between people and software systems
        autobernese.data_transfer -> external_data_sources "Get data"

        user -> autobernese.cli "Create campaign"
        user -> autobernese.cli "Get data from external sources"
        user -> autobernese.cli "Prepare input data + QA"
        user -> autobernese.cli "Run BSW campaign"
        user -> autobernese.cli "Quality control"
        user -> autobernese.cli "Prepare and publish end products"

        # user -> file_system "Get and move end products to own PC"

        autobernese.cli -> autobernese.data_transfer "Download data"

        # autobernese.cli -> autobernese.preprocessor.qaqc "Check data integrity, accessibility, etc."
        # autobernese.cli -> autobernese.preprocessor.qaqc "Perform quality assurance/control on end products"

        autobernese.cli -> autobernese.preprocessor "Rebuild general input data" ""
        autobernese.cli -> autobernese.preprocessor "Transfer relevant input data to the campaign directory"

        autobernese.cli -> autobernese.bsw "Create new campaign of given type" "NKG, 5D, KDI, RTK service"
        autobernese.cli -> autobernese.bsw "Convert sitelog to station file"
        autobernese.cli -> autobernese.bsw "Start BPE using campaign-specific PCF file"

        # autobernese.cli -> fire_api "Upload results to FIRE Database" ".CRD and .VEL files"

        # Relationships between containers
        autobernese.data_transfer -> file_system "Store external data locally"
        autobernese.bsw -> file_system "Store workspace and end products"
        autobernese.preprocessor.qaqc -> file_system "Assure quality of end products."
        autobernese.bsw -> bsw "Organise campaign and run BPE"

        # Relationships between components
        # TBW
        # Here will come the interactions between the different parts on the component level.
        autobernese.preprocessor.sitelog2sta_runner -> autobernese.preprocessor.sitelog2sta "Run converter for a given sitelog."
    }

    views {

        systemlandscape "systemlandscape" {
            include *
            # animation {
            #     file_system
            # }
        }

        systemContext autobernese "context-autobernese" {
            include *
        }

        container autobernese "container-autobernese" {
            include *
        }

        component autobernese.data_transfer "component-data" {
            include *
        }

        component autobernese.bsw "component-bsw" {
            include *
        }

        theme default

        styles {
            element "Group" {
                color #ff0000
            }
        }
    }

}
