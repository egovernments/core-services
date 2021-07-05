package egov.mailbot.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import egov.mailbot.models.Action;
import egov.mailbot.models.AttachmentProcessingException;
import egov.mailbot.models.Mapping;
import egov.mailbot.models.notification.Attachment;
import egov.mailbot.models.notification.EmailNotificationRequest;
import egov.mailbot.utils.Utils;
import lombok.extern.slf4j.Slf4j;
import org.egov.common.contract.request.RequestInfo;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.FileSystemResource;
import org.springframework.http.*;
import org.springframework.stereotype.Component;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.RestTemplate;

import java.nio.file.Path;
import java.util.Base64;

@Component
@Slf4j
public class DataUploadAttachmentProcessor implements AttachmentProcessor{

    @Autowired
    private RestTemplate restTemplate;

    @Autowired
    private ObjectMapper mapper;

    private final String url;

    public DataUploadAttachmentProcessor(RestTemplate restTemplate, ObjectMapper mapper,
                                         @Value("${data.upload.host}") String host,
                                         @Value("${data.upload.context.path}") String context) {
        this.restTemplate = restTemplate;
        this.mapper = mapper;

        this.url = host + context;
    }

    @Override
    public void processAttachments(EmailNotificationRequest notificationRequest, Mapping mapping, Path path) throws AttachmentProcessingException {
        mapper.configure(SerializationFeature.FAIL_ON_EMPTY_BEANS, false);

            String uriPath = mapping.getAdditionalFields().get("uriPaths").asText();
            String url = this.url + uriPath;
                try {
                    LinkedMultiValueMap<String, Object> map = new LinkedMultiValueMap<>();
                    map.add("file", new FileSystemResource(path));
                    map.add("requestInfo", getEncodedRequestInfo(notificationRequest.getRequestInfo()));

                    HttpHeaders headers = new HttpHeaders();
                    headers.setContentType(MediaType.MULTIPART_FORM_DATA);

                    HttpEntity<LinkedMultiValueMap<String, Object>> requestEntity = new HttpEntity<>(map, headers);
                    ResponseEntity<JsonNode> result = restTemplate.exchange(
                            url, HttpMethod.POST, requestEntity,
                            JsonNode.class);

                    if(result.getBody() != null) {
                        String fileStoreId = result.getBody().at("/fileStoreId").asText();
                        log.info("FILESTORE ID: "+ fileStoreId);
                        notificationRequest.getEmail().setAttachment(new Attachment(notificationRequest.getRequestInfo().getUserInfo().getTenantId(), fileStoreId));
                    }
                    log.info("Data upload completed with response code: "+result.getStatusCode());
                }catch (HttpClientErrorException e) {
                    log.error("Unable to process file!", e);
                    throw new AttachmentProcessingException(Utils.getErrorMessages(e.getResponseBodyAsString()));
                } catch (Exception e) {
                    log.error("Failed to process file!", e);
                    throw new AttachmentProcessingException("Failed to process attachment due to an unexpected error " +
                            "on the server!");
                }
    }

    @Override
    public Action action() {
        return Action.DATA_UPLOAD;
    }

    private String getEncodedRequestInfo(RequestInfo requestInfo){
        String json = null;
        try {
            json = mapper.writeValueAsString(requestInfo);
            return new String(Base64.getEncoder().encode(json.getBytes()));
        } catch (JsonProcessingException ignore) {
        }
        return "";
    }
}
