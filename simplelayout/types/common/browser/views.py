from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from simplelayout.base.interfaces import IBlockConfig, IScaleImage
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.i18n import translate


#dummy for refactoring
_ = lambda x: x

class paragraphView(BrowserView):
    template = ViewPageTemplateFile('paragraph_version_view.pt')
    def __call__(self):
        context = aq_inner(self.context).aq_explicit
        #auto redirect to the anchor
        param = '/#%s' % context.id

        return self.context.REQUEST.RESPONSE.redirect(
            context.aq_parent.absolute_url() + param)

    @property
    def macros(self):
        return {'main':self.template.macros['main']}


class FileView(BrowserView):
    def __init__(self, context, request):
        super(FileView, self).__init__(context, request)
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.sl_portal_url = self.portal_state.portal_url()
        self.parent = aq_parent(aq_inner(self.context))


class BlockView(BrowserView):

    def __init__(self, context, request):
        super(BlockView, self).__init__(context, request)
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.sl_portal_url = self.portal_state.portal_url()
        blockconf = IBlockConfig(self.context)
        self.image_layout = blockconf.image_layout

    def getCSSClass(self):
        layout = self.image_layout
        if layout is None:
            return 'sl-img-no-image'
        cssclass = 'sl-img-'+layout
        return cssclass

    def checkForImage(self):
        #check for a 'image' field in schemata
        if getattr(self.context.aq_explicit,'getImage',False):
            if self.context.getImage():
                return True
        return False

    def getImageTag(self):
        alt = unicode(self.context.getImageAltText(),
                      self.context.getCharset())
        title = unicode(self.context.getImageCaption(),
                        self.context.getCharset())

        is_clickable = hasattr(self.context, 'getImageClickable') and \
            self.context.getImageClickable() or False
        post_alt = translate(_(u'opens in new window'), context=self.request)
        if (is_clickable and len(alt)):
            alt = "%s (%s)" % (alt, post_alt)
        elif(is_clickable and not len(alt)):
            alt = "%s"%post_alt

        if not title:
            title = alt

        if getattr(self.context.aq_explicit,'getContact',False):
            return self.context.getContact().getField('foto').tag(
                self.context.getContact(),
                scale='thumbnail',
                alt=alt,
                title = alt
                )

        blockconf = IBlockConfig(self.context)
        scale = blockconf.image_scale
        dimension = blockconf.image_dimension

        #this peace of code is just for the first hit, otherwise we have
        # to write a migration.
        if not dimension:
            image_util = getUtility(IScaleImage,
                                    name='simplelayout.image.scaler')
            scale,dimension =  image_util.getScaledImageTag(self.context)
            blockconf.image_scale = scale
            blockconf.image_dimension = dimension

        width, height = blockconf.image_dimension
        return self.context.getField('image').tag(self.context,
                                                  scale=blockconf.image_scale,
                                                  width=width,
                                                  height=height,
                                                  alt=alt,
                                                  title = alt
                                                  )

    def image_wrapper_style(self):
        """ sets width of the div wrapping the image, so the
        caption linebreaks
        """

        blockconf = IBlockConfig(self.context)
        width, height = blockconf.image_dimension
        return "width: %spx" % width

    def getBlockHeight(self):
        blockconf = IBlockConfig(self.context)
        return blockconf.block_height or ''

    @property
    def wtool(self):
        return getToolByName(self.context, 'portal_workflow')


class ImageView(BrowserView):

    def __init__(self, context, request):
        super(BrowserView, self).__init__(context, request)
        blockconf = IBlockConfig(self.context)
        self.image_layout = blockconf.image_layout

    def getCSSClass(self):
        layout = self.image_layout
        if layout is None:
            return 'sl-img-no-image'
        cssclass = 'sl-img-'+layout
        return cssclass


    def getImageTag(self):
        #title = unicode(self.context.Title(), self.context.getCharset())
        title = hasattr(self.context, 'imageAlternativeText') and \
            self.context.imageAlternativeText or ''
        alt = title
        blockconf = IBlockConfig(self.context)

        scale = blockconf.image_scale
        dimension = blockconf.image_dimension
        # this peace of code is just for the first hit, otherwise
        # we have to write a migration.
        if not dimension:
            image_util = getUtility(IScaleImage,
                                    name='simplelayout.image.scaler')
            scale,dimension =  image_util.getScaledImageTag(self.context,
                                                            'image')
            blockconf.image_scale = scale
            blockconf.image_dimension = dimension

        width, height = blockconf.image_dimension
        return self.context.getField('image').tag(self.context,
                                                  scale=blockconf.image_scale,
                                                  width=width,
                                                  height=height,
                                                  alt=alt,
                                                  title=title
                                                  )

    def showTitleOfImage(self):
        show_image_title = hasattr(self.context, 'showImageTitle') and \
            self.context.showImageTitle or False
        return show_image_title
