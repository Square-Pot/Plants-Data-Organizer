
import os
import datetime
from pylibdmtx.pylibdmtx import encode
from PIL import Image, ImageEnhance
from fpdf import FPDF

from .folders import FolderStructure

DATA_MATRIX_SIZE = 30   # px
LABEL_LENGHT = 80       # mm
NEXT_COLUMN_X = 90      # mm
VERTICAL_SPACE = 6      # mm
START_X = 10            # mm 
START_Y = 10            # mm


class Label:
    def __init__(self):
        self.puid = None
        self.dmtx = None
        self.field_number = None
        self.genus = None
        self.species = None
        self.subspecies = None
        self.variety = None
        self.cultivar = None
        self.affinity = None
        self.ex = None
        self.text_lines = []
        self.ppmm = 2.7                                             # pixels per mm
        self.dmtx_side_px = DATA_MATRIX_SIZE                        # assumed that dmtx is square and sides are euqal
        self.dmtx_side_mm = DATA_MATRIX_SIZE // self.ppmm
        self.full_length = LABEL_LENGHT

    def extract_data(self, rich_plant):
        """Fill current object with data from RichPlant"""
        self.puid =         str(rich_plant.uid)
        self.field_number = rich_plant.number.strip().upper()                 if rich_plant.number else None
        
        # Line 1 data
        self.genus =        rich_plant.genus.strip().capitalize()             if rich_plant.genus else None
        self.species =      rich_plant.species.strip().lower()                if rich_plant.species else None
        self.subspecies =   rich_plant.subspecies.strip().lower()             if rich_plant.subspecies else None
        
        # Line 2 data
        self.variety =      rich_plant.variety.strip().lower()                if rich_plant.variety else None
        self.cultivar =     rich_plant.cultivar.strip().title()               if rich_plant.cultivar else None

        # Line 3 data
        self.affinity =     rich_plant.affinity.strip().title()               if rich_plant.affinity else None
        self.ex =           rich_plant.ex.strip().title()                     if rich_plant.ex else None
        self.source =       rich_plant.source.strip()                         if rich_plant.source else None

        self._generate_text_lines()
        self._generate_datamatrix()

    def get_lines_number(self):
        """Returns number of text lines in label"""
        return len(self.text_lines)

    def get_width(self):
        return self.dmtx_side_px

    def _generate_text_lines(self):
        """Generating text lines according to data"""
        # Line 1 generating
        if self.genus and self.species and self.subspecies:
            text_line_1 = f'**__{self.genus[0]}.__** __{self.species}__  ssp. __{self.subspecies}__'
        else:
            text_line_1 = ''
            text_line_1 += f'**__{self.genus}__** ' if self.genus else ''
            text_line_1 += f'__{self.species}__ ' if self.species else ''
            text_line_1 += f'ssp. __{self.subspecies}__ ' if self.subspecies else ''
        if text_line_1: 
            self.text_lines.append(text_line_1)

        # Line 2 generating
        text_line_2 = ''
        text_line_2 += f'v. __{self.variety}__ ' if self.variety else ''
        text_line_2 += f'cv. ‘{self.cultivar}’ ' if self.cultivar else ''
        
        if text_line_2: 
            self.text_lines.append(text_line_2)

        # Line 3 generating
        text_line_3 = ''
        text_line_3 += f'aff. {self.affinity} ' if self.affinity else ''
        text_line_3 += f'ex. {self.ex} ' if self.ex else ''
        text_line_3 += f'[{self.source}]' if self.source else ''
        if text_line_3:
            self.text_lines.append(text_line_3)

        # Placeholder if no data
        if len(self.text_lines) == 0:
            self.text_lines.append('_' * 20)
            self.text_lines.append('_' * 20)



    def _generate_datamatrix(self):
        """Data matrix image generating"""
        encoded = encode(self.puid.encode('ASCII'))
        dmtx_img = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels)                  # Image size is 70x70 px, where margins are 10px
        dmtx_img = dmtx_img.crop((10, 10 , 60, 60))                                                         # Crop white margins. Resulting image size is: 50x50 px
        #dmtx_img = dmtx_img.resize((self.dmtx_side_px, self.dmtx_side_px), resample=PIL.Image.LANCZOS)     
        dmtx_img = dmtx_img.resize((self.dmtx_side_px, self.dmtx_side_px))                                   # Resize to IMG_WIDTH square. Think what TODO when this matrix-size will exhaust
        enhancer = ImageEnhance.Contrast(dmtx_img)
        final_dmtx_img = enhancer.enhance(1.5)
        self.dmtx = final_dmtx_img


class LabelsBuilder:
    def __init__(self, folders:FolderStructure, rich_plants:list):
        self.rich_plants = rich_plants
        self.page_high = 297                                    # high of A4 
        self.v_space = VERTICAL_SPACE                           # vertical space between labels
        self.start_x = START_X                                  # x of origin
        self.start_y = START_Y                                  # y of origin 
        self.column_shift = NEXT_COLUMN_X
        self.show_brd = 0                                       # showing of borders in cells for debugging
        self.field_num_cell_width = 6
        self.pdf = self._create_pdf()
        self.cur_x = self.start_x
        self.cur_y = self.start_y
        self.cur_column = 1

        folders.check_pdf_labels_folder()
        self.output_folder = folders.get_pdf_label_folder()

    def _create_pdf(self) -> FPDF:
        """PDF-object create and setup"""
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font('dejavu', 'B', fname='app/fonts/DejaVuSansCondensed-Bold.ttf', uni=True)
        pdf.add_font('dejavu', 'BI',  fname='app/fonts/DejaVuSansCondensed-BoldOblique.ttf', uni=True)
        pdf.add_font('dejavu', 'I', fname='app/fonts/DejaVuSansCondensed-Oblique.ttf', uni=True)
        pdf.add_font('dejavu', fname='app/fonts/DejaVuSansCondensed.ttf', uni=True)
        pdf.set_font('dejavu', size=10)
        return pdf

    def _get_label_position(self, label:Label):
        """Y-position calculation for current label"""
        label_heigh = label.get_width()
        v_space_left = self.page_high - self.cur_y              # free space left in the bottom of the page

        if v_space_left - label_heigh -self.v_space < 10:
            if self.cur_column == 1:
                self.cur_y = self.start_y
                self.cur_x = self.start_x + self.column_shift
                self.cur_column = 2
            elif self.cur_column == 2:
                self.pdf.add_page()
                self.cur_x = self.start_x
                self.cur_y = self.start_y
                self.cur_column = 1
        else: 
            if self.cur_column == 1:
                self.cur_x = self.start_x
                if self.cur_y == self.start_y:
                    pass
                else:
                    self.cur_y += self.v_space
            elif self.cur_column == 2:
                self.cur_x = self.start_x + self.column_shift
                self.cur_y += self.v_space

        self._xy_update()

    def _xy_update(self, shift_x=0, shift_y=0):
        """
            Updating position with current x,y values
            Additional shift is possible
        """
        self.pdf.set_xy(self.cur_x + shift_x, self.cur_y + shift_y)

    def _place_dmtx(self, label:Label):
        """Placing data matrix image"""
        self.pdf.image(label.dmtx, x=self.cur_x, y=self.cur_y)
        self.cur_x += label.dmtx_side_mm

    def _place_frame(self, label:Label):
        """Placing frame around all label (except data matrix)"""
        horiz_shift = 1                                         # space between data matrix and frame
        self._xy_update(shift_x=horiz_shift)
        frame_heigh = label.dmtx_side_mm                        # high of label is equal to size of data matrix
        frame_width = label.full_length - label.dmtx_side_mm 
        self.pdf.cell(frame_width, frame_heigh, '', border=1)
        
    def _place_field_number(self, label:Label):
        """Placing rotaded field number"""
        self.cur_y += label.dmtx_side_mm
        self._xy_update()
        self.pdf.set_font_size(8)
        heigh = label.dmtx_side_mm                              # high of field number cell is equal to size of data matrix
        width = self.field_num_cell_width
        text = f'{label.field_number}' if label.field_number else ''
        with self.pdf.rotation(90):
            self.pdf.cell(heigh, width, text, border=self.show_brd, align="C")

    def _place_text_lines(self, label:Label):
        """Placing text lines"""
        self.cur_x += self.field_num_cell_width
        self.cur_y -= label.dmtx_side_mm
        self._xy_update()

        self.pdf.set_font_size(8)
        heigh = label.dmtx_side_mm / label.get_lines_number()
        width = label.full_length - label.dmtx_side_mm - self.field_num_cell_width

        for cnt, text in enumerate(label.text_lines, start=1) :
            if cnt > 2:
                self.pdf.set_font('dejavu', '', 8)
            else:
                self.pdf.set_font('dejavu', '', 10)
            self.pdf.cell(width, heigh, text, border=self.show_brd, markdown=True)
            self.cur_y += heigh
            self._xy_update()
        self.pdf.set_font('dejavu', '', 10)

    def generate_labels(self):
        """Generate list of Labels objects"""
        for rp in self.rich_plants:
            label = Label()
            label.extract_data(rp)
            self._get_label_position(label)

            self._place_dmtx(label)
            self._place_frame(label)
            self._place_field_number(label)
            self._place_text_lines(label)

            self.cur_x = self.pdf.get_x()
            self.cur_y = self.pdf.get_y()

    def get_pdf(self):
        """Generating PDF-file"""
        dt_stamp = datetime.datetime.now().strftime('%d-%m-%Y_%H-%M-%S_%f')
        filename = f'Labels_{dt_stamp}.pdf'
        fullpath = os.path.join(self.output_folder, filename)
        self.pdf.output(fullpath, 'F')
        return fullpath
