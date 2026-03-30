import streamlit as st
import asyncio
import os
import yaml
import tempfile
import json
from io import BytesIO
import zipfile

from src.core.orchestrator import BatchOrchestrator
from src.core.api_client import ApiClient
from src.retailers.ambrose_parser import AmbroseParser
from src.retailers.brooksbrothers_parser import BrooksBrothersParser
from src.retailers.croma_parser import CromaParser
from src.retailers.dillards_parser import DillardsParser
from src.retailers.evo_parser import EvoParser
from src.retailers.fashionworld_parser import FashionWorldParser
from src.retailers.jcrew_parser import JcrewParser
from src.retailers.jdwilliams_parser import JDWilliamsParser
from src.retailers.joefresh_parser import JoeFreshParser
from src.retailers.lenovo_parser import LenovoParser
from src.retailers.lenovolas_parser import LenovoLasParser
from src.retailers.napaonline_parser import NapaOnlineParser
from src.retailers.simplybe_parser import SimplyBeParser
from src.retailers.solesupplier_parser import SoleSupplierParser
from src.retailers.revzilla_parser import RevzillaParser
from src.retailers.uniquevintage_parser import UniqueVintageParser
from src.retailers.homeessentials_parser import HomeEssentialsParser
from src.retailers.pacsun_parser import PacsunParser
from src.retailers.lenovointelus_parser import LenovoIntelUsParser
from src.retailers.lenovointelall_parser import LenovoIntelAllParser
from src.retailers.lululemon_parser import LululemonParser
from src.retailers.janieandjack_parser import JanieAndJackParser
from src.retailers.loft_parser import LoftParser
from src.retailers.athleta_parser import AthletaParser
from src.retailers.petsupermarket_parser import PetSuperMarketParser
from src.retailers.image_parser import ImageParser
from src.retailers.jacamo_parser import JacamoParser
from src.retailers.anntaylor_parser import AnnTaylorParser
from src.retailers.staples_parser import StaplesParser
from src.retailers.vincecamuto_parser import VinceCamutoParser
from src.retailers.quiksilver_parser import QuiksilverParser
from src.retailers.billabong_parser import BillabongParser
from src.retailers.lenovoglobalar_parser import LenovoGlobalArParser
from src.retailers.lenovoglobalcl_parser import LenovoGlobalClParser
from src.retailers.lenovoglobalco_parser import LenovoGlobalCoParser
from src.retailers.lenovoglobalmx_parser import LenovoGlobalMxParser
from src.retailers.lenovoglobalpe_parser import LenovoGlobalPeParser
from src.retailers.lenovoglobalsg_parser import LenovoGlobalSgParser
from src.retailers.reebok_parser import ReebokParser
from src.retailers.lenovoglobalie_parser import LenovoGlobalIeParser
from src.retailers.lenovoglobalgb_parser import LenovoGlobalGbParser
from src.retailers.lenovoglobalhk_parser import LenovoGlobalHkParser
from src.retailers.lenovoglobalca_parser import LenovoGlobalCaParser
from src.retailers.lenovoglobalin_parser import LenovoGlobalInParser
from src.retailers.lenovoglobalau_parser import LenovoGlobalAuParser
from src.retailers.roots_parser import RootsParser
from src.retailers.bananarepublic_parser import BananaRepublicParser
from src.retailers.bananarepublicfactory_parser import BananaRepublicParser as BananaRepublicFactoryParser
from src.retailers.solesupplierv2_parser import SoleSupplierV2
from src.retailers.footlocker_parser import FootLockerParser
from src.retailers.madewell_parser import MadewellParser
from src.retailers.gapfactoryus_parser import GapFactoryUsParser
from src.retailers.gapus_parser import GapUsParser
from src.retailers.oldnavyca_parser import OldNavyCaParser
from src.retailers.alexandani_parser import AlexAndAniParser
from src.retailers.davidjones_parser import DavidJonesParser
from src.retailers.bananarepubliccanada_parser import BananaRepublicCanadaParser
from src.retailers.gapca_parser import GapCaParser
from src.retailers.dickssportinggoods_parser import DicksSportingGoodsParser
from src.retailers.snapone_en_us_parser import SnapOneEnUsParser


RETAILER_PARSERS = {
    "ambrose": AmbroseParser,
    "brooksbrothers": BrooksBrothersParser,
    "croma": CromaParser,
    "dillards": DillardsParser,
    "evo": EvoParser,
    "fashionworld": FashionWorldParser,
    "jcrew": JcrewParser,
    "jdwilliams": JDWilliamsParser,
    "joefresh": JoeFreshParser,
    "lenovo": LenovoParser,
    "lenovolas": LenovoLasParser,
    "napaonline": NapaOnlineParser,
    "simplybe": SimplyBeParser,
    "solesupplier": SoleSupplierParser,
    "revzilla": RevzillaParser,
    "uniquevintage": UniqueVintageParser,
    "homeessentials": HomeEssentialsParser,
    "pacsun": PacsunParser,
    "lenovointelus": LenovoIntelUsParser,
    "lenovointelall": LenovoIntelAllParser,
    "lululemon": LululemonParser,
    "janieandjack": JanieAndJackParser,
    "loft": LoftParser,
    "athleta": AthletaParser,
    "petsupermarket": PetSuperMarketParser,
    "image": ImageParser,
    "jacamo": JacamoParser,
    "anntaylor": AnnTaylorParser,
    "staples": StaplesParser,
    "vincecamuto": VinceCamutoParser,
    "quiksilver": QuiksilverParser,
    "billabong": BillabongParser,
    "lenovoglobalar": LenovoGlobalArParser,
    "lenovoglobalcl": LenovoGlobalClParser,
    "lenovoglobalco": LenovoGlobalCoParser,
    "lenovoglobalmx": LenovoGlobalMxParser,
    "lenovoglobalpe": LenovoGlobalPeParser,
    "lenovoglobalsg": LenovoGlobalSgParser,
    "reebok": ReebokParser,
    "lenovoglobalie": LenovoGlobalIeParser,
    "lenovoglobalgb": LenovoGlobalGbParser,
    "lenovoglobalhk": LenovoGlobalHkParser,
    "lenovoglobalca": LenovoGlobalCaParser,
    "lenovoglobalin": LenovoGlobalInParser,
    "lenovoglobalau": LenovoGlobalAuParser,
    "roots": RootsParser,
    "bananarepublic": BananaRepublicParser,
    "bananarepublicfactory": BananaRepublicFactoryParser,
    "solesupplierv2": SoleSupplierV2,
    "footlocker": FootLockerParser,
    "madewell": MadewellParser,
    "gapfactoryus": GapFactoryUsParser,
    "gapus": GapUsParser,
    "oldnavyca": OldNavyCaParser,
    "alexandani": AlexAndAniParser,
    "davidjones": DavidJonesParser,
    "bananarepubliccanada": BananaRepublicCanadaParser,
    "gapca": GapCaParser,
    "dickssportinggoods": DicksSportingGoodsParser,
    "snapone_en_us": SnapOneEnUsParser,
}


def create_zip_file(file_paths):
    """Creates a ZIP file containing all the given file paths."""
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for file_path in file_paths:
            zip_file.write(file_path, os.path.basename(file_path))
    zip_buffer.seek(0)
    return zip_buffer


def run_orchestrator(keywords, retailer_name, num_output_files):
    """Runs the BatchOrchestrator with the given inputs."""
    config = None
    # Look for config relative to this file's parent (qa_tools root)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for extension in ("yaml", "yml"):
        config_path = os.path.join(base_dir, "configs", f"{retailer_name}.{extension}")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
            break

    if config is None:
        raise FileNotFoundError(
            f"Configuration file not found for '{retailer_name}'. "
            "Expected configs/<retailer>.yaml or configs/<retailer>.yml"
        )

    temp_dir = tempfile.TemporaryDirectory()
    config["output_dir"] = temp_dir.name
    config["output_filename_base"] = f"{retailer_name}_results"
    config["num_output_files"] = num_output_files
    config["input_csv_path"] = None

    ParserClass = RETAILER_PARSERS[retailer_name]
    data_parser = ParserClass(config)
    api_client = ApiClient(config["retry_settings"])
    orchestrator = BatchOrchestrator(config, api_client, data_parser)
    orchestrator.keywords = keywords

    asyncio.run(orchestrator.run())

    output_files = [
        os.path.join(config["output_dir"], file)
        for file in os.listdir(config["output_dir"])
        if file.endswith(".json")
    ]
    return output_files, temp_dir


def render_data_fetcher():
    """Renders the Data Fetcher for LLM Assortment Analysis tool."""

    st.header("📦 Data Fetcher for LLM Assortment")
    st.markdown(
        "Batch-fetch product data from retailer APIs for LLM assortment analysis. "
        "Select a retailer, paste keywords, and download structured JSON output."
    )

    # Initialize session state
    if "df_output_files" not in st.session_state:
        st.session_state.df_output_files = None
    if "df_output_dir" not in st.session_state:
        st.session_state.df_output_dir = None

    retailer_name = st.selectbox(
        "Select Retailer", options=list(RETAILER_PARSERS.keys()), key="df_retailer"
    )
    keywords_input = st.text_area("Paste Keywords (one per line)", key="df_keywords")
    num_output_files = st.number_input(
        "Number of Output Files", min_value=1, value=1, step=1, key="df_num_files"
    )

    if st.button("Run", key="df_run_btn"):
        # Cleanup previous run
        if st.session_state.df_output_dir:
            try:
                st.session_state.df_output_dir.cleanup()
            except Exception as e:
                st.warning(f"Failed to cleanup previous temporary directory: {e}")
            finally:
                st.session_state.df_output_files = None
                st.session_state.df_output_dir = None

        if not keywords_input.strip():
            st.error("Please paste at least one keyword.")
        else:
            keywords = [kw.strip() for kw in keywords_input.splitlines() if kw.strip()]
            st.info(f"Processing {len(keywords)} keywords for retailer '{retailer_name}'...")

            try:
                output_files, temp_dir_obj = run_orchestrator(keywords, retailer_name, num_output_files)
                st.session_state.df_output_files = output_files
                st.session_state.df_output_dir = temp_dir_obj
                st.rerun()
            except Exception as e:
                st.error(f"An error occurred: {e}")
                if st.session_state.df_output_dir:
                    try:
                        st.session_state.df_output_dir.cleanup()
                    except Exception as cleanup_error:
                        st.warning(f"Could not clean up temp directory during error handling: {cleanup_error}")
                st.session_state.df_output_files = None
                st.session_state.df_output_dir = None

    if st.session_state.df_output_files:
        st.success("Processing complete! Download your files below:")
        for file_path in st.session_state.df_output_files:
            with open(file_path, "r") as f:
                file_data = f.read()
            st.download_button(
                label=f"Download {os.path.basename(file_path)}",
                data=file_data,
                file_name=os.path.basename(file_path),
                mime="application/json",
                key=f"df_dl_{os.path.basename(file_path)}",
            )

        zip_buffer = create_zip_file(st.session_state.df_output_files)
        st.download_button(
            label="Download All Files as ZIP",
            data=zip_buffer,
            file_name=f"{retailer_name}_results.zip",
            mime="application/zip",
            key="df_dl_zip",
        )
